# auto_topic_modeler.py

import logging
import os
from typing import List

import pandas as pd
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from bertopic.vectorizers import ClassTfidfTransformer
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AutoTopicModeler:
    """
    A class to handle automatic topic modeling using BERTopic.
    """

    def __init__(self):
        """
        Initializes the AutoTopicModeler with a given configuration.
        """
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        logging.info("Embedding model initialized.")
        self.topic_model = self.initialize_bertopic_model()
        logging.info("BERTopic model initialized.")
        self.embeddings = None  # To store document embeddings

    def initialize_bertopic_model(self) -> BERTopic:
        """Initialize and return a BERTopic model with the given configuration."""
        umap_model = UMAP(
            n_neighbors=3,
            n_components=2,
            min_dist=0.05,
            metric="cosine",
            random_state=42
        )
        hdbscan_model = HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric="euclidean",
            prediction_data=True
        )
        vectorizer_model = CountVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_df=1.0,
            min_df=1,
            max_features=5000
        )
        ctfidf_model = ClassTfidfTransformer(
            reduce_frequent_words=True
        )
        representation_model = KeyBERTInspired(top_n_words=10)

        topic_model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            ctfidf_model=ctfidf_model,
            representation_model=representation_model,
            nr_topics="auto",
            top_n_words=10,
            calculate_probabilities=True,
            verbose=True
        )
        return topic_model

    def fit_model(self, docs: List[str]):
        """
        Fits the BERTopic model to the provided documents.

        Parameters:
        docs (List[str]): A list of document texts.
        """
        if not all(isinstance(doc, str) for doc in docs):
            raise TypeError("All documents must be strings.")

        logging.info("Fitting BERTopic model to documents...")
        self.topics, self.probabilities = self.topic_model.fit_transform(docs)
        self.topic_info = self.topic_model.get_topic_info()
        logging.info("BERTopic model fitting completed.")

        # Extract embeddings
        self.embeddings = self.embedding_model.encode(docs, convert_to_numpy=True)
        logging.info("Document embeddings generated.")

    def assign_topic_names(self):
        """
        Assigns readable topic names based on the topic information.
        """
        logging.info("Assigning readable topic names...")
        # Create a mapping from topic numbers to descriptive names
        self.topic_name_mapping = {
            row["Topic"]: " ".join(row["Name"].split("_")[1:3]) if row["Name"] != "No Topic" else "No Topic"
            for _, row in self.topic_info.iterrows()
        }

        # Replace topic numbers with descriptive names
        self.topic_names = [self.topic_name_mapping.get(topic, "No Topic") for topic in self.topics]
        logging.info("Topic names assigned.")

    def get_topic_assignments(self) -> List[str]:
        """
        Returns the list of assigned topic names for each document.

        Returns:
        List[str]: Assigned topic names.
        """
        return self.topic_names

    def get_embeddings(self) -> List[List[float]]:
        """
        Returns the embeddings of the documents.

        Returns:
        List[List[float]]: A list of embedding vectors.
        """
        if self.embeddings is None:
            logging.error("Embeddings have not been generated. Call fit_model first.")
            return []
        return self.embeddings.tolist()

    def export_results(self, docs: List[str], output_dir: str = "bertopic_results"):
        """
        Exports the topic modeling results to CSV files.

        Parameters:
        docs (List[str]): The list of document texts.
        output_dir (str): Directory to save the CSV files.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        df_topics = pd.DataFrame(self.topic_info)
        df_documents = pd.DataFrame({
            "Document": docs,
            "Topic": self.topic_names
        })

        df_topics.to_csv(os.path.join(output_dir, "topic_info.csv"), index=False)
        df_documents.to_csv(os.path.join(output_dir, "document_assignments.csv"), index=False)
        logging.info(f"BERTopic results exported to '{output_dir}' directory.")

    # def visualize_topics(self, output_dir: str = "bertopic_results"):
    #     """
    #     Visualizes the topics using BERTopic's built-in visualization tools.
    #
    #     Parameters:
    #     output_dir (str): Directory to save the visualization files.
    #     """
    #     import os
    #     if not os.path.exists(output_dir):
    #         os.makedirs(output_dir)
    #
    #     # Visualize topics
    #     fig = self.topic_model.visualize_topics()
    #     fig.write_html(os.path.join(output_dir, "topics.html"))
    #     logging.info(f"Topic visualization saved to '{output_dir}/topics.html'.")
    #
    #     # You can add more visualizations as needed

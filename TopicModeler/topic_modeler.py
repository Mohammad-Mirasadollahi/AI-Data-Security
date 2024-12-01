# topic_modeler.py

import logging
from typing import List, Tuple

import numpy as np
import torch
from sentence_transformers import SentenceTransformer


class TopicModeler:
    """
    A class to handle topic modeling and label assignment.
    """

    def __init__(self, predefined_topics: List[str],
                 embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initializes the TopicModeler with predefined topics and embedding model.

        Parameters:
        predefined_topics (List[str]): List of predefined topic names.
        embedding_model_name (str): Name of the sentence transformer model.
        """
        self.predefined_topics = predefined_topics
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self._configure_device()

    def _configure_device(self):
        """
        Configures the device for the embedding model to use GPU if available.
        """
        if torch.cuda.is_available():
            self.embedding_model.to("cuda")
            logging.info("SentenceTransformer model moved to GPU.")
        else:
            self.embedding_model.to("cpu")
            logging.info("SentenceTransformer model is using CPU.")

    def assign_predefined_labels(self, embeddings: np.ndarray) -> Tuple[List[str], List[float]]:
        """
        Assigns labels based on predefined topics and document embeddings.

        Parameters:
        embeddings (np.ndarray): Embeddings of the documents.

        Returns:
        Tuple[List[str], List[float]]: Assigned labels and their corresponding confidence scores.
        """
        try:
            logging.info("Starting label assignment based on predefined topics.")
            if not self.predefined_topics:
                raise ValueError("No predefined topics provided.")

            # Encode predefined topics
            topic_label_embeddings = self.embedding_model.encode(
                self.predefined_topics, show_progress_bar=False
            )
            logging.debug("Predefined topic embeddings computed.")

            # Normalize embeddings
            embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            topic_label_embeddings_norm = topic_label_embeddings / np.linalg.norm(topic_label_embeddings, axis=1,
                                                                                  keepdims=True)

            # Calculate cosine similarity
            similarities = np.dot(embeddings_norm, topic_label_embeddings_norm.T)
            logging.debug("Cosine similarity between documents and topics computed.")

            # Assign labels
            assigned_labels = []
            confidences = []
            for sim in similarities:
                idx = np.argmax(sim)
                assigned_labels.append(self.predefined_topics[idx])
                confidences.append(sim[idx])

            logging.info("Label assignment completed successfully.")
            return assigned_labels, confidences

        except Exception as e:
            logging.error(f"Error during label assignment: {e}")
            raise

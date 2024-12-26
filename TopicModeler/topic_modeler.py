# topic_modeler.py

import logging
from typing import List, Tuple, Dict, Optional

import numpy as np
import torch
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

from Utils.utils import chunk_document


class TopicModeler:
    """
    A class to handle topic modeling and label assignment with main categories and subcategories.
    """

    def __init__(
            self,
            predefined_topics: Dict[str, List[str]],
            embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            kw_model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initializes the TopicModeler with predefined topics (including subcategories),
        embedding model, and keyword extraction model.

        Parameters:
        predefined_topics (Dict[str, List[str]]): Dictionary of main topics and their subcategories.
        embedding_model_name (str): Name of the SentenceTransformer model.
        kw_model_name (str): Name of the KeyBERT embedding model.
        """
        self.predefined_topics = predefined_topics
        self.main_topics = list(predefined_topics.keys())
        self.sub_topics = {main: subs for main, subs in predefined_topics.items()}
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self._configure_device()

        # Initialize KeyBERT model
        self.kw_model = KeyBERT(model=kw_model_name)

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

    def extract_keywords(self, doc: str, top_n: int = 10, chunk_size: int = 1000) -> List[str]:
        """
        Extracts keywords from a document using KeyBERT with document chunking.

        Parameters:
        doc (str): The document text.
        top_n (int): Number of top keywords to extract per chunk.
        chunk_size (int): The maximum number of characters per chunk.

        Returns:
        List[str]: List of extracted keywords.
        """
        try:
            # Split the document into smaller chunks
            chunks = chunk_document(doc, chunk_size=chunk_size)
            logging.debug(f"Document divided into {len(chunks)} chunks.")

            all_keywords = []
            for chunk in chunks:
                keywords = self.kw_model.extract_keywords(
                    chunk,
                    keyphrase_ngram_range=(1, 3),
                    use_maxsum=True,
                    use_mmr=True,
                    diversity=0.5,
                    top_n=top_n
                )
                extracted_keywords = [kw for kw, score in keywords]
                all_keywords.extend(extracted_keywords)
                logging.debug(f"Extracted keywords from chunk: {extracted_keywords}")

            # Remove duplicate keywords while preserving order
            unique_keywords = list(dict.fromkeys(all_keywords))
            logging.debug(f"Unique keywords after combining chunks: {unique_keywords}")
            return unique_keywords
        except Exception as e:
            logging.error(f"Keyword extraction failed: {e}")
            return []

    def assign_labels(self, embeddings: np.ndarray) -> Tuple[List[str], List[Optional[str]], List[float]]:
        """
        Assigns main categories and subcategories based on embeddings.

        Parameters:
        embeddings (np.ndarray): Embeddings of the documents.

        Returns:
        Tuple[List[str], List[Optional[str]], List[float]]: Assigned main categories, subcategories, and confidence scores.
        """
        try:
            # Assign main categories
            main_labels, main_confidences = self.assign_predefined_labels(embeddings, self.main_topics)

            # Assign subcategories based on main categories
            sub_labels = []
            sub_confidences = []
            for idx, main_label in enumerate(main_labels):
                sub_topic_list = self.sub_topics.get(main_label, [])
                if not sub_topic_list:
                    sub_labels.append(None)
                    sub_confidences.append(0.0)
                    continue
                sub_embeddings = self.embedding_model.encode(sub_topic_list, show_progress_bar=False)
                # Normalize
                embedding_norm = embeddings[idx] / np.linalg.norm(embeddings[idx])
                sub_embeddings_norm = sub_embeddings / np.linalg.norm(sub_embeddings, axis=1, keepdims=True)
                similarity = np.dot(sub_embeddings_norm, embedding_norm)
                sub_idx = np.argmax(similarity)
                sub_labels.append(sub_topic_list[sub_idx])
                sub_confidences.append(similarity[sub_idx])

            return main_labels, sub_labels, main_confidences

        except Exception as e:
            logging.error(f"Error during label assignment: {str(e)}")
            raise

    def assign_predefined_labels(self, embeddings: np.ndarray, topics: List[str]) -> Tuple[List[str], List[float]]:
        """
        Assigns labels based on predefined topics and document embeddings.

        Parameters:
        embeddings (np.ndarray): Embeddings of the documents.
        topics (List[str]): List of topic names (either main or sub).

        Returns:
        Tuple[List[str], List[float]]: Assigned labels and their corresponding confidence scores.
        """
        try:
            logging.info("Starting label assignment based on predefined topics.")
            if not topics:
                raise ValueError("No predefined topics provided.")

            # Encode predefined topics
            topic_label_embeddings = self.embedding_model.encode(
                topics, show_progress_bar=False
            )
            logging.debug("Predefined topic embeddings computed.")

            # Normalize embeddings
            embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            topic_label_embeddings_norm = topic_label_embeddings / np.linalg.norm(topic_label_embeddings, axis=1,
                                                                                  keepdims=True)

            # Calculate cosine similarity
            similarities = np.dot(embeddings_norm, topic_label_embeddings_norm.T)
            logging.debug("Cosine similarity between documents and topics computed.")

            # Assign labels based on highest similarity
            assigned_labels = []
            confidences = []
            for sim in similarities:
                idx = np.argmax(sim)
                assigned_labels.append(topics[idx])
                confidences.append(sim[idx])

            logging.info("Label assignment completed successfully.")
            return assigned_labels, confidences

        except Exception as e:
            logging.error(f"Error during label assignment: {str(e)}")
            raise

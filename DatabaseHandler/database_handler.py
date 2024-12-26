# database_handler.py

# DatabaseHandler/database_handler.py

import logging
from typing import List, Dict, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer


class DatabaseHandler:
    """
    A class to manage the connection to the Qdrant database and perform operations related to documents.
    """

    def __init__(self, host: str, port: int, api_key: Optional[str] = None, collection_name: str = "documents"):
        """
        Initializes the DatabaseHandler by connecting to Qdrant and setting up the desired collection.

        Parameters:
        host (str): Qdrant host.
        port (int): Qdrant port.
        api_key (Optional[str]): API key if required.
        collection_name (str): Name of the collection in Qdrant.
        """
        self.collection_name = collection_name
        try:
            self.client = QdrantClient(url=f"{host}:{port}")
            self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            logging.info("Connected to Qdrant.")
        except Exception as e:
            logging.error(f"Failed to connect to Qdrant: {e}")
            raise

        # Ensure the collection exists
        try:
            if not self.client.collection_exists(collection_name=self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={"size": 384, "distance": "Cosine"}
                )
                logging.info(f"Created collection '{self.collection_name}'.")
            else:
                logging.info(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logging.error(f"Failed to ensure collection existence: {e}")
            raise

    def insert_documents(self, documents: List[Dict]):
        """
        Inserts documents into the Qdrant collection.

        Parameters:
        documents (List[Dict]): A list of dictionaries containing document information.
        """

        try:
            points = []
            for idx, doc in enumerate(documents):
                print(f"this is :{doc['text']}")
                point = PointStruct(
                    id=idx,
                    vector=doc['embedding'],
                    payload={
                        "file_name": doc['file_name'],
                        "topic": doc['topic'],
                        "sub_topic": doc.get('sub_topic', ''),
                        "sha256": doc['sha256'],
                        "fuzzy_hash": doc['fuzzy_hash'],
                        "file_type": doc['file_type'],
                        "text": doc['text']
                    }
                )
                points.append(point)
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logging.info(f"Inserted {len(documents)} documents into '{self.collection_name}' collection.")
        except Exception as e:
            logging.error(f"Failed to insert documents into Qdrant: {e}")
            raise

    def generate_query_vector(self, query_text: str) -> List[float]:
        """
        Generates an embedding vector for the query text.

        Parameters:
        query_text (str): The query text.

        Returns:
        List[float]: The embedding vector.
        """
        try:
            return self.embedding_model.encode(query_text).tolist()
        except Exception as e:
            logging.error(f"Failed to generate query vector: {e}")
            raise

    def get_statistics(self) -> dict:
        """
        Retrieves statistics from the Qdrant collection, including counts for main topics and subtopics.

        Returns:
        dict: A dictionary containing document statistics.
        """
        try:
            # Get total document count
            total = self.client.count(collection_name=self.collection_name).count

            # Initialize topic and subtopic counts
            topics = {}
            subtopics = {}

            # Retrieve all documents using pagination
            offset = 0
            limit = 1000  # Adjust based on needs

            while True:
                # Perform a vector search with a dummy query vector to retrieve all documents
                dummy_vector = np.zeros(384).tolist()
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=dummy_vector,
                    limit=limit,
                    offset=offset,
                    with_payload=True
                )

                if not search_result:
                    break

                for point in search_result:
                    topic = point.payload.get('topic', 'Unknown')
                    sub_topic = point.payload.get('sub_topic', 'Unknown')

                    # Count main topics
                    if topic in topics:
                        topics[topic] += 1
                    else:
                        topics[topic] = 1

                    # Count subtopics
                    if sub_topic in subtopics:
                        subtopics[sub_topic] += 1
                    else:
                        subtopics[sub_topic] = 1

                offset += limit

            statistics = {
                "total_documents": total,
                "documents_per_topic": topics,
                "documents_per_subtopic": subtopics
            }
            logging.info("Retrieved statistics from Qdrant.")
            return statistics
        except Exception as e:
            logging.error(f"Failed to retrieve statistics from Qdrant: {e}")
            raise

    def search_documents_by_vector(self, query_text: str, topic: str = "", limit: int = 10) -> List[Dict]:
        """
        Searches for documents based on vector similarity, with optional topic and text filters.

        Parameters:
        query_text (str): The query text.
        topic (str): The topic to filter documents by (optional).
        limit (int): The number of results to return.

        Returns:
        List[Dict]: A list of documents matching the search criteria.
        """
        try:
            # Generate query vector
            query_vector = self.generate_query_vector(query_text)
            if not isinstance(query_vector, list):
                raise ValueError("The query vector must be a list of floats.")

            # Build search filter based on topic
            search_filter = {}
            if topic:
                search_filter["must"] = [
                    {
                        "key": "topic",
                        "match": {
                            "value": topic
                        }
                    }
                ]

            # Perform vector search using the query vector and filters
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )

            # Extract documents from search results
            documents = []
            for point in search_result:
                documents.append({
                    "file_name": point.payload.get('file_name'),
                    "topic": point.payload.get('topic'),
                    "sub_topic": point.payload.get('sub_topic'),
                    "sha256": point.payload.get('sha256'),
                    "fuzzy_hash": point.payload.get('fuzzy_hash'),
                    "file_type": point.payload.get('file_type'),
                    "text": point.payload.get('text')
                })

            logging.info(f"Found {len(documents)} documents matching the query.")
            return documents

        except Exception as e:
            logging.error(f"Failed to search documents by vector: {e}")
            raise

    def get_all_documents(self) -> List[Dict]:
        """
        Retrieves all documents from the Qdrant collection.

        Returns:
        List[Dict]: A list of all documents with their metadata.
        """
        try:
            documents = []
            limit = 1000  # Adjust based on needs
            offset = 0

            while True:
                # Use a dummy query vector to retrieve all documents
                dummy_vector = np.zeros(384).tolist()
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=dummy_vector,
                    limit=limit,
                    offset=offset,
                    with_payload=True
                )

                if not search_result:
                    break

                for point in search_result:
                    documents.append({
                        "file_name": point.payload.get('file_name'),
                        "topic": point.payload.get('topic'),
                        "sub_topic": point.payload.get('sub_topic'),
                        "sha256": point.payload.get('sha256'),
                        "fuzzy_hash": point.payload.get('fuzzy_hash'),
                        "file_type": point.payload.get('file_type'),
                        "text": point.payload.get('text')
                    })

                offset += limit

            logging.info(f"Retrieved all {len(documents)} documents from Qdrant.")
            return documents

        except Exception as e:
            logging.error(f"Failed to retrieve all documents from Qdrant: {e}")
            raise

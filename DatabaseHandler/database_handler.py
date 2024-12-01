import logging

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer


class DatabaseHandler:
    def __init__(self, host: str, port: int, api_key=None, collection_name: str = "documents"):
        self.collection_name = collection_name
        try:
            self.client = QdrantClient(url=f"{host}:{port}")
            self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            logging.info("Connected to Qdrant.")
        except Exception as e:
            logging.error(f"Failed to connect to Qdrant: {e}")
            raise

        # Ensure collection exists
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

    def insert_documents(self, documents: list):
        try:
            points = []
            for idx, doc in enumerate(documents):
                point = PointStruct(
                    id=idx,
                    vector=doc['embedding'],
                    payload={
                        "file_name": doc['file_name'],
                        "topic": doc['topic'],
                        "text": doc['text'],
                        "file_type": doc['file_type']
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

    def generate_query_vector(self, query_text: str):
        """Generate vector (embedding) for the query text."""
        return self.embedding_model.encode(query_text).tolist()

    def get_statistics(self) -> dict:
        try:
            # Retrieve total document count
            total = self.client.count(collection_name=self.collection_name).count

            # Retrieve documents in batches using pagination with search
            limit = 1000  # Adjust the limit based on your needs
            offset = 0  # Start from the first point

            # Store topics count
            topics = {}

            while True:
                # Use a query vector with dimension 384 (e.g., all zeros for no vector-based search)
                query_vector = np.zeros(384).tolist()  # Placeholder vector of zeros, dimension 384
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,  # Empty query vector for retrieval (no specific query)
                    limit=limit,
                    offset=offset
                )

                # Ensure points are returned, otherwise break the loop
                if isinstance(search_result, list):  # Check if the result is a list (not a dictionary)
                    points = search_result
                else:
                    points = search_result.get('points', [])

                if not points:  # If no points are returned, stop the loop
                    break

                # Process the points
                for point in points:
                    topic = point.payload.get('topic', 'Unknown')
                    topics[topic] = topics.get(topic, 0) + 1

                offset += limit  # Increment offset for the next batch

            statistics = {"total_documents": total, "documents_per_topic": topics}
            logging.info("Retrieved statistics from Qdrant.")
            return statistics
        except Exception as e:
            logging.error(f"Failed to retrieve statistics from Qdrant: {e}")
            raise

    def search_documents_by_vector(self, topic: str = "", query_text: str = "", limit: int = 10) -> list:
        """
        Search for documents by vector similarity, with optional topic and text filters.

        Parameters:
        query_vector (list): The vector representing the search query.
        topic (str): The topic to filter documents by (optional).
        query_text (str): The text to match (optional, for boosting the relevance of the search).
        limit (int): The number of results to return.

        Returns:
        list: A list of documents matching the search criteria.
        """
        try:
            # If query_text is provided, generate query vector from it
            if query_text:
                query_vector = self.generate_query_vector(query_text)  # Ensure this returns a list of floats
            print(query_vector)
            # If query_vector is a string, this is an issue since Qdrant expects a list of floats.
            if isinstance(query_vector, str):
                raise ValueError("The query vector must be a list of floats, not a string.")

            # Ensure query_vector is a list or numpy array before proceeding
            if isinstance(query_vector, list):
                query_vector = np.array(query_vector)  # Convert to numpy array
            query_vector = query_vector.tolist()  # Ensure it's a list of floats

            # Build the search filter based on topic and query_text
            search_filter = {}
            if topic:
                search_filter["must"] = [
                    {
                        "key": "topic",  # Searching by topic
                        "match": {
                            "value": topic  # The topic to match
                        }
                    }
                ]

            # Perform the vector search using the query_vector and the filters
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,  # Pass query vector directly
                query_filter=search_filter,  # Pass the built filter
                limit=limit  # Set the limit for the number of results
            )

            # Extract the relevant points from the search results
            print(search_result)  # This will print the structure of search_result

            # Extract the points from the search result (assuming it is a list of ScoredPoint objects)
            points = search_result.get('result', []) if isinstance(search_result, dict) else search_result

            # Extract the relevant points from the search results
            documents = []
            for point in points:
                # Access properties using dot notation
                documents.append({
                    "file_name": point.payload.get('file_name'),  # Access payload attribute
                    "topic": point.payload.get('topic'),
                    "text": point.payload.get('text'),
                    "file_type": point.payload.get('file_type')
                })

            logging.info(f"Found {len(documents)} documents matching the query.")
            return documents

        except Exception as e:
            logging.error(f"Failed to search documents by vector: {e}")
            raise

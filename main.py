# main.py

import logging
import os
import shutil
from typing import List

from DatabaseHandler.database_handler import DatabaseHandler
from DocumentLoader.document_loader import DocumentLoader
from TopicModeler.topic_modeler import TopicModeler


def setup_logging(log_folder: str, log_file: str = 'document_loader.log'):
    """
    Sets up logging configuration.

    Parameters:
    log_folder (str): Path to the log folder.
    log_file (str): Name of the log file.
    """
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, log_file)

    # Configure logging only if no handlers are present
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    logging.info("Logging configured.")


def process_documents(predefined_topics: List[str], input_folder: str, output_folder: str, db_handler: DatabaseHandler):
    """
    Processes documents: load, encode, assign topics, store in DB, organize output folders.

    Parameters:
    predefined_topics (List[str]): List of predefined topics.
    input_folder (str): Path to input folder containing documents.
    output_folder (str): Path to output folder to organize documents by topic.
    db_handler (DatabaseHandler): Instance of DatabaseHandler to interact with Qdrant.
    """
    logger = logging.getLogger(__name__)

    # Initialize DocumentLoader
    document_loader = DocumentLoader(logger=logger)
    file_names, documents = document_loader.load_documents(input_folder)

    if not documents:
        logger.error("No documents to process. Exiting.")
        return

    num_documents = len(documents)
    logger.info(f"Number of documents loaded: {num_documents}")

    # Initialize TopicModeler with predefined topics
    topic_modeler = TopicModeler(predefined_topics=predefined_topics)
    logger.info("TopicModeler initialized with predefined topics.")

    # Encode documents
    try:
        document_embeddings = topic_modeler.embedding_model.encode(documents, show_progress_bar=True)
        logger.info("Document embeddings encoded successfully.")
    except Exception as e:
        logger.error(f"Failed to encode documents: {e}")
        return

    # Assign predefined labels
    try:
        assigned_labels, confidences = topic_modeler.assign_predefined_labels(document_embeddings)
        logger.info("Assigned predefined labels to documents successfully.")
    except Exception as e:
        logger.error(f"Failed to assign labels: {e}")
        return

    # Prepare documents for database insertion
    documents_to_insert = []
    for file_name, topic, text, embedding in zip(file_names, assigned_labels, documents, document_embeddings):
        file_type = os.path.splitext(file_name)[1].lower()
        documents_to_insert.append({
            "file_name": file_name,
            "topic": topic,
            "text": text,
            "file_type": file_type,
            "embedding": embedding.tolist()  # Convert numpy array to list for JSON serialization
        })

    # Insert documents into Qdrant
    try:
        db_handler.insert_documents(documents_to_insert)
        logger.info("Inserted documents into Qdrant successfully.")
    except Exception as e:
        logger.error(f"Failed to insert documents into database: {e}")
        return

    # Organize documents into output folder subdirectories by topic
    try:
        os.makedirs(output_folder, exist_ok=True)
        for file_name, topic in zip(file_names, assigned_labels):
            src_path = os.path.join(input_folder, file_name)
            dest_folder = os.path.join(output_folder, topic)
            dest_path = os.path.join(dest_folder, file_name)
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            logger.info(f"Copied '{file_name}' to '{dest_folder}'.")
        logger.info("Document organization and storage complete.")
    except Exception as e:
        logger.error(f"Failed to organize documents into folders: {e}")

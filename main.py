# main.py

import logging
import os
import shutil
from typing import List, Dict

from DatabaseHandler.database_handler import DatabaseHandler
from DocumentLoader.document_loader import DocumentLoader
from TopicModeler.topic_modeler import TopicModeler


def setup_logging(log_folder: str, log_file: str = 'document_processor.log'):
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


def process_documents(predefined_topics: Dict[str, List[str]], input_folder: str, output_folder: str,
                      db_handler: DatabaseHandler):
    """
    Processes documents: load, encode, assign topics, store in DB, organize output folders.

    Parameters:
    predefined_topics (Dict[str, List[str]]): Dictionary of predefined main topics and their subcategories.
    input_folder (str): Path to input folder containing documents.
    output_folder (str): Path to output folder to organize documents by topic.
    db_handler (DatabaseHandler): Instance of DatabaseHandler to interact with Qdrant.
    """
    logger = logging.getLogger(__name__)

    # Initialize DocumentLoader
    document_loader = DocumentLoader(log_file=os.path.join('logs', 'document_loader.log'))
    file_names, documents = document_loader.load_documents(input_folder)

    if not documents:
        logger.error("No documents to process. Exiting.")
        return

    num_documents = len(documents)
    logger.info(f"Number of documents loaded: {num_documents}")

    # Initialize TopicModeler with predefined topics
    topic_modeler = TopicModeler(predefined_topics=predefined_topics)
    logger.info("TopicModeler initialized with predefined topics.")

    # Extract keywords
    try:
        extracted_keywords_list = []
        for idx, doc in enumerate(documents):
            keywords = topic_modeler.extract_keywords(doc["text"], top_n=10, chunk_size=1000)
            extracted_keywords = ' '.join(keywords)  # Combine keywords into a single string
            logger.info(f"Extracted keywords from '{doc['file_name']}': {extracted_keywords}")
            extracted_keywords_list.append(extracted_keywords)
        logger.info("Keyword extraction completed successfully.")
    except Exception as e:
        logger.error(f"Failed to extract keywords: {e}")
        return

    # Encode the extracted keywords
    try:
        keyword_embeddings = topic_modeler.embedding_model.encode(
            extracted_keywords_list, show_progress_bar=True
        )
        logger.info("Keyword embeddings encoded successfully.")
    except Exception as e:
        logger.error(f"Failed to encode keyword embeddings: {e}")
        return

    # Assign labels to documents (main topics and subtopics)
    try:
        main_labels, sub_labels, main_confidences = topic_modeler.assign_labels(keyword_embeddings)
        logger.info("Assigned predefined labels to documents successfully.")
    except Exception as e:
        logger.error(f"Failed to assign labels: {e}")
        return

    # Prepare documents for database insertion
    documents_to_insert = []
    for file_name, topic, sub_topic, doc, embedding in zip(file_names, main_labels, sub_labels, documents,
                                                           keyword_embeddings):
        file_type = os.path.splitext(file_name)[1].lower().strip('.')
        documents_to_insert.append({
            "file_name": file_name,
            "topic": topic,
            "sub_topic": sub_topic if sub_topic else "",
            "text": doc['text'],
            "file_type": file_type,
            "sha256": document_loader.documents[file_names.index(file_name)]['sha256'],
            "fuzzy_hash": document_loader.documents[file_names.index(file_name)]['fuzzy_hash'],
            "embedding": embedding.tolist()  # Convert numpy array to list for JSON serialization
        })

    # Insert documents into Qdrant
    try:
        db_handler.insert_documents(documents_to_insert)
        logger.info("Inserted documents into Qdrant successfully.")
    except Exception as e:
        logger.error(f"Failed to insert documents into database: {e}")
        return

    # Organize documents into output folder subdirectories by topic and subtopic
    try:
        os.makedirs(output_folder, exist_ok=True)
        for doc in documents_to_insert:
            file_name = doc['file_name']
            main_topic = doc['topic']
            sub_topic = doc['sub_topic']
            src_path = os.path.join(input_folder, file_name)

            if sub_topic:
                dest_folder = os.path.join(output_folder, main_topic, sub_topic)
            else:
                dest_folder = os.path.join(output_folder, main_topic)

            dest_path = os.path.join(dest_folder, file_name)
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            logger.info(f"Copied '{file_name}' to '{dest_folder}'.")
        logger.info("Document organization and storage complete.")
    except Exception as e:
        logger.error(f"Failed to organize documents into folders: {e}")


if __name__ == "__main__":
    # Define input and output folder paths
    input_folder = "input_documents"  # Replace with your input folder path
    output_folder = "./organized_documents"  # Replace with your output folder path

    # Define main categories and subcategories
    predefined_topics = {
        "Security": [
            "Cybersecurity",
            "Mobile Security",
            "Operating System Security",
            # ... other subcategories
        ],
        "Health": [
            "Public Health",
            "Mental Health",
            # ... other subcategories
        ],
        # ... other main categories
    }

    # Qdrant connection parameters
    qdrant_host = "127.0.0.1"  # Qdrant host
    qdrant_port = 6333  # Qdrant port
    collection_name = "documents"  # Qdrant collection name

    # Ensure output and log directories exist
    try:
        os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        print(f"Failed to create output folder '{output_folder}': {e}")
        exit(1)

    try:
        os.makedirs("logs", exist_ok=True)
    except Exception as e:
        print(f"Failed to create logs folder: {e}")
        exit(1)

    # Setup logging
    setup_logging(log_folder="logs", log_file='document_processor.log')

    # Initialize DatabaseHandler
    try:
        db_handler = DatabaseHandler(
            host=qdrant_host,
            port=qdrant_port,
            collection_name=collection_name
        )
    except Exception as e:
        logging.error(f"Failed to initialize DatabaseHandler: {e}")
        exit(1)

    # Execute the processing function
    process_documents(
        predefined_topics=predefined_topics,
        input_folder=input_folder,
        output_folder=output_folder,
        db_handler=db_handler
    )

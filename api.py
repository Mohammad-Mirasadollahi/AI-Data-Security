import logging
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import your existing modules
from DatabaseHandler.database_handler import DatabaseHandler
from config import Config
from main import (
    setup_logging,
    process_documents,
    process_auto_topics
)


# ----------------------------
# 1. Define Pydantic models
# ----------------------------

class PredefinedTopicsRequest(BaseModel):
    """
    Request model for processing documents with predefined topics.
    """
    predefined_topics: Dict[str, List[str]]
    input_folder: str
    output_folder: str


class AutoTopicsRequest(BaseModel):
    """
    Request model for processing documents with automatic topic modeling.
    """
    input_folder: str
    output_folder: str


class SearchRequest(BaseModel):
    """
    Request model for searching documents by topic and a query text.
    """
    topic: str
    query_text: str
    limit: Optional[int] = 10


class DocumentResponse(BaseModel):
    """
    A response model for a single document.
    Adjust fields as needed.
    """
    file_name: str
    topic: Optional[str] = None
    sub_topic: Optional[str] = None
    file_type: Optional[str] = None
    sha256: Optional[str] = None
    fuzzy_hash: Optional[str] = None
    text: Optional[str] = None


# -----------------------------------
# 2. Initialize FastAPI application
# -----------------------------------

app = FastAPI(
    title="Document Processing API",
    description="API to process and categorize documents (Predefined or Automatic Topics).",
    version="1.0.0"
)


# ----------------------------
# 3. Application Startup
# ----------------------------

@app.on_event("startup")
def on_startup():
    """
    Runs on application startup.
    1. Initializes logging.
    2. Connects to Qdrant (via DatabaseHandler).
    3. Stores references in app.state for reuse.
    """
    # Load config
    config = Config()

    # Ensure log folder exists
    os.makedirs(config.log_folder, exist_ok=True)
    # Initialize logging
    setup_logging(config.log_folder, log_file='document_processor.log')
    logging.info("FastAPI application startup: Logging is configured.")

    # Initialize DatabaseHandler
    try:
        db_handler = DatabaseHandler(
            host=config.qdrant_host,
            port=config.qdrant_port,
            api_key=config.qdrant_api_key,
            collection_name="documents"
        )
        app.state.db_handler = db_handler
        logging.info("DatabaseHandler initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize DatabaseHandler: {e}")
        raise RuntimeError(f"Database connection failed: {e}")


# ----------------------------
# 4. Endpoints
# ----------------------------

@app.get("/healthcheck", summary="Check API health status")
def healthcheck():
    """
    Simple health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is running."}


# --- Predefined Topics Processing ---

@app.post("/process/predefined", summary="Process documents with predefined topics")
def process_predefined_documents(request: PredefinedTopicsRequest):
    """
    Process documents using predefined main topics and subtopics.
    - Loads documents from `request.input_folder`.
    - Categorizes them based on `request.predefined_topics`.
    - Saves categorized documents to `request.output_folder`.
    - Inserts document info into Qdrant.
    """
    logger = logging.getLogger(__name__)

    # Validate input folder
    if not os.path.isdir(request.input_folder):
        logger.error(f"Invalid input folder: {request.input_folder}")
        raise HTTPException(status_code=400, detail="Invalid input folder path.")

    # Validate output folder
    if not request.output_folder:
        logger.error("No output folder provided.")
        raise HTTPException(status_code=400, detail="Output folder path not provided.")
    os.makedirs(request.output_folder, exist_ok=True)

    # Process documents
    try:
        db_handler = app.state.db_handler
        process_documents(
            predefined_topics=request.predefined_topics,
            input_folder=request.input_folder,
            output_folder=request.output_folder,
            db_handler=db_handler
        )
        logger.info("Completed document processing with predefined topics.")
        return {"message": "Document processing with predefined topics completed successfully."}
    except Exception as e:
        logger.error(f"Error during predefined topics processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Automatic Topics Processing ---

@app.post("/process/auto", summary="Process documents with automatic topic modeling")
def process_automatic_documents(request: AutoTopicsRequest):
    """
    Process documents using automatic topic modeling (BERTopic or similar).
    - Loads documents from `request.input_folder`.
    - Automatically discovers topics and organizes documents.
    - Saves categorized documents to `request.output_folder`.
    - Inserts document info into Qdrant.
    """
    logger = logging.getLogger(__name__)

    # Validate input folder
    if not os.path.isdir(request.input_folder):
        logger.error(f"Invalid input folder: {request.input_folder}")
        raise HTTPException(status_code=400, detail="Invalid input folder path.")

    # Validate output folder
    if not request.output_folder:
        logger.error("No output folder provided.")
        raise HTTPException(status_code=400, detail="Output folder path not provided.")
    os.makedirs(request.output_folder, exist_ok=True)

    # Process documents with automatic topic modeling
    try:
        db_handler = app.state.db_handler
        process_auto_topics(
            input_folder=request.input_folder,
            output_folder=request.output_folder,
            db_handler=db_handler
        )
        logger.info("Completed document processing with automatic topics.")
        return {"message": "Document processing with automatic topics completed successfully."}
    except Exception as e:
        logger.error(f"Error during automatic topics processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Retrieve Database Statistics ---

@app.get("/statistics", summary="Get statistics from the Qdrant database")
def get_statistics():
    """
    Retrieves statistics such as:
      - total_documents
      - documents_per_topic
      - documents_per_subtopic
    """
    logger = logging.getLogger(__name__)
    try:
        db_handler = app.state.db_handler
        stats = db_handler.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Retrieve All Documents ---

@app.get("/documents", summary="Get all documents in the database", response_model=List[DocumentResponse])
def get_all_documents():
    """
    Returns all documents in the Qdrant database.
    For demonstration, we limit the fields in the response model with `DocumentResponse`.
    """
    logger = logging.getLogger(__name__)
    try:
        db_handler = app.state.db_handler
        all_docs = db_handler.get_all_documents()

        # If you want to limit or transform the text field (e.g., truncated), do it here:
        for doc in all_docs:
            if 'text' in doc and len(doc['text']) > 500:
                doc['text'] = doc['text'][:500] + "..."

        return all_docs
    except Exception as e:
        logger.error(f"Failed to load documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))




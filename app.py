# app.py

import logging
import os

import pandas as pd
import streamlit as st

from DatabaseHandler.database_handler import DatabaseHandler
from config import Config
from main import setup_logging, process_documents  # Import functions from main.py


# Initialize logging for the Streamlit app
def initialize_logging(log_folder: str, log_file: str = 'document_loader.log'):
    """
    Initializes logging for the Streamlit app.

    Parameters:
    log_folder (str): Path to the log folder.
    log_file (str): Name of the log file.
    """
    setup_logging(log_folder, log_file)  # Utilize setup_logging from main.py


# Main Streamlit app function
def main():
    # Load configurations (optional, can be used for default values)
    config = Config()

    # Initialize logging
    initialize_logging(config.log_folder)
    logger = logging.getLogger(__name__)

    st.title("Document Processing and Categorization Tool")
    st.write("Upload documents, assign topics, and manage your document database.")

    st.header("1. Input Configuration")

    with st.form("config_form"):
        st.subheader("Predefined Topics")
        predefined_topics_input = st.text_area(
            "Enter predefined topics (one per line):",
            height=200,
            help="Provide each topic on a separate line."
        )

        st.subheader("Input Folder Path")
        input_folder = st.text_input(
            "Enter the path to the input folder containing documents:",
            value=config.input_folder,
            help="Specify the directory where your documents are stored."
        )

        st.subheader("Output Folder Path")
        output_folder = st.text_input(
            "Enter the path to the output folder:",
            value=config.output_folder,
            help="The directory where categorized documents will be stored."
        )

        submit_button = st.form_submit_button(label='Start Processing')

    if submit_button:
        # Process predefined topics and check validity
        predefined_topics = [topic.strip() for topic in predefined_topics_input.strip().split('\n') if topic.strip()]
        if not predefined_topics:
            st.error("Please provide at least one predefined topic.")
            logger.error("No predefined topics provided by the user.")
        elif not input_folder or not os.path.isdir(input_folder):
            st.error("Please provide a valid input folder path.")
            logger.error(f"Invalid input folder path provided: {input_folder}")
        else:
            if not output_folder:
                st.error("Please provide a valid output folder path.")
                logger.error("No output folder path provided by the user.")
            else:
                # Initialize DatabaseHandler
                try:
                    db_handler = DatabaseHandler(
                        host=config.qdrant_host,
                        port=config.qdrant_port,
                        api_key=config.qdrant_api_key,
                        collection_name="documents"
                    )
                except Exception as e:
                    st.error(f"Failed to initialize DatabaseHandler: {e}")
                    logger.error(f"Failed to initialize DatabaseHandler: {e}")
                    return

                # Process Documents
                with st.spinner('Processing documents...'):
                    process_documents(predefined_topics, input_folder, output_folder, db_handler)
                st.success('Document processing and categorization completed successfully!')
                logger.info("Document processing and categorization completed successfully.")

    st.header("2. Database Statistics")

    if st.button("Load Statistics"):
        try:
            db_handler = DatabaseHandler(
                host=config.qdrant_host,
                port=config.qdrant_port,
                api_key=config.qdrant_api_key,
                collection_name="documents"
            )
            statistics = db_handler.get_statistics()
            st.write(f"**Total Documents:** {statistics['total_documents']}")
            st.write("**Documents per Topic:**")
            df_stats = pd.DataFrame(list(statistics['documents_per_topic'].items()), columns=['Topic', 'Count'])
            st.dataframe(df_stats)
        except Exception as e:
            st.error(f"Failed to retrieve statistics: {e}")
            logger.error(f"Failed to retrieve statistics: {e}")

    st.header("3. Search Documents by Topic")

    db_handler = None
    try:
        db_handler = DatabaseHandler(
            host=config.qdrant_host,
            port=config.qdrant_port,
            api_key=config.qdrant_api_key,
            collection_name="documents"
        )
    except Exception as e:
        st.error(f"Failed to connect to the database: {e}")
        logger.error(f"Failed to connect to the database: {e}")

    if db_handler:
        try:
            # Fetch topics from the database statistics
            statistics = db_handler.get_statistics()
            topics = list(statistics['documents_per_topic'].keys())
            selected_topic = st.selectbox("Select a topic to search:", topics)

            # Add a text input for the user to write a query text
            query_text = st.text_area("Write a text to search similar documents:", height=150)

            if st.button("Search"):
                with st.spinner(f"Searching for documents in topic: {selected_topic}..."):
                    documents = db_handler.search_documents_by_vector(topic=selected_topic, query_text=query_text)
                if documents:
                    st.write(f"**Found {len(documents)} documents in topic '{selected_topic}':**")
                    for doc in documents:
                        st.markdown(f"### {doc['file_name']}")
                        st.markdown(f"**Type:** {doc['file_type']}")
                        st.markdown(f"**Topic:** {doc['topic']}")
                        st.markdown(f"**Content Preview:** {doc['text'][:500]}...")  # Show first 500 characters
                        st.markdown("---")
                else:
                    st.info(f"No documents found for topic '{selected_topic}'.")
        except Exception as e:
            st.error(f"Failed to search documents: {e}")
            logger.error(f"Failed to search documents: {e}")


# Run the main function
if __name__ == "__main__":
    main()

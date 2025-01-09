# app.py

import logging
import os

import pandas as pd
import streamlit as st

from DatabaseHandler.database_handler import DatabaseHandler
from config import Config
from main import setup_logging, process_documents, process_auto_topics  # Import both processing functions from main.py


# Initialize logging for the Streamlit app
def initialize_logging(log_folder: str, log_file: str = 'document_processor.log'):
    """
    Initializes logging for the Streamlit app.

    Parameters:
    log_folder (str): Path to the log folder.
    log_file (str): Name of the log file.
    """
    setup_logging(log_folder, log_file)  # Utilize setup_logging from main.py


# Function to initialize session state
def initialize_session_state():
    if 'topics' not in st.session_state:
        st.session_state.topics = []


# Function to add a new main topic
def add_main_topic():
    st.session_state.topics.append({'main_topic': '', 'subtopics': []})


# Function to remove a main topic
def remove_main_topic(index):
    del st.session_state.topics[index]


# Function to add a subtopic to a main topic
def add_subtopic(index):
    st.session_state.topics[index]['subtopics'].append('')


# Function to remove a subtopic from a main topic
def remove_subtopic(main_index, sub_index):
    del st.session_state.topics[main_index]['subtopics'][sub_index]


# Main Streamlit app function
def main():
    # Load configurations (optional, can be used for default values)
    config = Config()

    # Initialize session state
    initialize_session_state()

    # Initialize logging
    initialize_logging(config.log_folder)
    logger = logging.getLogger(__name__)

    st.title("Document Processing and Categorization Tool")
    st.write("Upload documents, assign topics, and manage your document database.")

    st.header("1. Processing Configuration")

    # Selection between Predefined Topics and Automatic Topics
    processing_mode = st.radio(
        "Select Processing Mode:",
        ("Predefined Topics", "Automatic Topics"),
        help="Choose between using predefined topics or automatic topic modeling."
    )

    if processing_mode == "Predefined Topics":
        st.subheader("Predefined Topics and Subcategories")

        # Button to add a new main topic
        if st.button("Add Main Topic"):
            add_main_topic()

        # Display all main topics and their subtopics
        for idx, topic in enumerate(st.session_state.topics):
            with st.expander(f"Main Topic {idx + 1}"):
                # Input for main topic name
                main_topic = st.text_input(
                    f"Main Topic {idx + 1}",
                    value=topic['main_topic'],
                    key=f"main_topic_{idx}"
                )
                st.session_state.topics[idx]['main_topic'] = main_topic

                # Button to add a subtopic
                if st.button(f"Add Subtopic to Main Topic {idx + 1}", key=f"add_subtopic_{idx}"):
                    add_subtopic(idx)

                # Display all subtopics for this main topic
                for sub_idx, subtopic in enumerate(topic['subtopics']):
                    col1, col2 = st.columns([8, 2])
                    with col1:
                        subtopic_input = st.text_input(
                            f"Subtopic {sub_idx + 1}",
                            value=subtopic,
                            key=f"subtopic_{idx}_{sub_idx}"
                        )
                        st.session_state.topics[idx]['subtopics'][sub_idx] = subtopic_input
                    with col2:
                        if st.button(
                                f"Remove Subtopic {sub_idx + 1}",
                                key=f"remove_subtopic_{idx}_{sub_idx}"
                        ):
                            remove_subtopic(idx, sub_idx)

                # Button to remove the main topic
                if st.button(f"Remove Main Topic {idx + 1}", key=f"remove_main_topic_{idx}"):
                    remove_main_topic(idx)

    st.subheader("Input and Output Folder Paths")

    # Input Folder Path
    input_folder = st.text_input(
        "Enter the path to the input folder containing documents:",
        value=config.input_folder,
        help="Specify the directory where your documents are stored."
    )

    # Output Folder Path
    output_folder = st.text_input(
        "Enter the path to the output folder:",
        value=config.output_folder,
        help="The directory where categorized documents will be stored."
    )

    # Button to Start Processing (Separate from the topic/subtopic dynamic interactions)
    if st.button('Start Processing'):
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
            st.stop()

        if processing_mode == "Predefined Topics":
            # Validate that all main topics and subtopics are filled
            valid = True
            for idx, topic in enumerate(st.session_state.topics):
                if not topic['main_topic']:
                    st.error(f"Main Topic {idx + 1} is empty.")
                    valid = False
                for sub_idx, subtopic in enumerate(topic['subtopics']):
                    if not subtopic:
                        st.error(f"Subtopic {sub_idx + 1} under Main Topic {idx + 1} is empty.")
                        valid = False
            if not valid:
                st.stop()

            # Process predefined topics and subcategories
            try:
                predefined_topics = {}
                for topic in st.session_state.topics:
                    main_topic = topic['main_topic']
                    subtopics = topic['subtopics']
                    predefined_topics[main_topic] = subtopics
                if not predefined_topics:
                    st.error("Please provide at least one predefined topic with subcategories.")
                    logger.error("No predefined topics provided by the user.")
                    st.stop()
            except Exception as e:
                st.error(f"Failed to parse predefined topics: {e}")
                logger.error(f"Failed to parse predefined topics: {e}")
                st.stop()

            # Validate input folder
            if not input_folder or not os.path.isdir(input_folder):
                st.error("Please provide a valid input folder path.")
                logger.error(f"Invalid input folder path provided: {input_folder}")
                st.stop()

            # Validate output folder
            if not output_folder:
                st.error("Please provide a valid output folder path.")
                logger.error("No output folder path provided by the user.")
                st.stop()

            # Process Documents
            with st.spinner('Processing documents with predefined topics...'):
                process_documents(predefined_topics, input_folder, output_folder, db_handler)
            st.success('Document processing and categorization with predefined topics completed successfully!')
            logger.info("Document processing and categorization with predefined topics completed successfully.")

        elif processing_mode == "Automatic Topics":
            # Validate input folder
            if not input_folder or not os.path.isdir(input_folder):
                st.error("Please provide a valid input folder path.")
                logger.error(f"Invalid input folder path provided: {input_folder}")
                st.stop()

            # Validate output folder
            if not output_folder:
                st.error("Please provide a valid output folder path.")
                logger.error("No output folder path provided by the user.")
                st.stop()

            # Process Automatic Topics
            with st.spinner('Processing documents with automatic topic modeling...'):
                process_auto_topics(input_folder, output_folder, db_handler)
            st.success('Document processing and categorization with automatic topics completed successfully!')
            logger.info("Document processing and categorization with automatic topics completed successfully.")

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

            st.write("**Documents per Main Topic:**")
            df_main_topics = pd.DataFrame(list(statistics['documents_per_topic'].items()),
                                          columns=['Main Topic', 'Count'])
            st.dataframe(df_main_topics)
            st.bar_chart(df_main_topics.set_index('Main Topic'))

            st.write("**Documents per Subtopic:**")
            df_subtopics = pd.DataFrame(list(statistics['documents_per_subtopic'].items()),
                                        columns=['Subtopic', 'Count'])
            st.dataframe(df_subtopics)
            st.bar_chart(df_subtopics.set_index('Subtopic'))

        except Exception as e:
            st.error(f"Failed to retrieve statistics: {e}")
            logger.error(f"Failed to retrieve statistics: {e}")

    st.header("3. Document Information")

    if st.button("Load All Documents"):
        try:
            db_handler = DatabaseHandler(
                host=config.qdrant_host,
                port=config.qdrant_port,
                api_key=config.qdrant_api_key,
                collection_name="documents"
            )
            all_documents = db_handler.get_all_documents()

            if all_documents:
                # Create a DataFrame from all_documents
                df_documents = pd.DataFrame(all_documents)

                # Select and reorder columns as desired
                desired_columns = ['file_name', 'topic', 'sub_topic', 'file_type', 'sha256', 'fuzzy_hash', 'text']
                df_documents = df_documents[desired_columns]

                # Rename columns for better readability
                df_documents.rename(columns={
                    'file_name': 'File Name',
                    'topic': 'Main Topic',
                    'sub_topic': 'Subtopic',
                    'file_type': 'File Type',
                    'sha256': 'SHA-256 Hash',
                    'fuzzy_hash': 'Fuzzy Hash',
                    'text': 'Content Preview'
                }, inplace=True)

                # Create a content preview by truncating the text
                df_documents['Content Preview'] = df_documents['Content Preview'].apply(
                    lambda x: x[:500] + '...' if len(x) > 500 else x
                )

                # Display the table
                st.dataframe(df_documents)

                # Optionally, add export functionality
                if st.button("Export Document Information as CSV"):
                    try:
                        csv = df_documents.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name='document_information.csv',
                            mime='text/csv',
                        )
                        st.success("Document information exported successfully!")
                    except Exception as e:
                        st.error(f"Failed to export CSV: {e}")
                        logger.error(f"Failed to export CSV: {e}")

            else:
                st.info("No documents found in the database.")
        except Exception as e:
            st.error(f"Failed to load documents: {e}")
            logger.error(f"Failed to load documents: {e}")

    st.header("4. Search Documents by Topic")

    # Initialize db_handler in session state to persist across interactions
    if 'db_handler' not in st.session_state:
        try:
            db_handler = DatabaseHandler(
                host=config.qdrant_host,
                port=config.qdrant_port,
                api_key=config.qdrant_api_key,
                collection_name="documents"
            )
            st.session_state.db_handler = db_handler
        except Exception as e:
            st.error(f"Failed to connect to the database: {e}")
            logger.error(f"Failed to connect to the database: {e}")
            st.session_state.db_handler = None

    if st.session_state.db_handler:
        try:
            db_handler = st.session_state.db_handler

            # Fetch topics from the database statistics
            statistics = db_handler.get_statistics()
            topics = list(statistics['documents_per_topic'].keys())
            if not topics:
                st.info("No topics found in the database to search.")
                st.stop()
            selected_topic = st.selectbox("Select a main topic to search:", topics)

            # Add a text input for the user to write a query text
            query_text = st.text_area("Write a text to search similar documents:", height=150)

            if st.button("Search"):
                if not query_text.strip():
                    st.error("Please enter some text to search.")
                    st.stop()
                with st.spinner(f"Searching for documents in topic: {selected_topic}..."):
                    documents = db_handler.search_documents_by_vector(
                        query_text=query_text,
                        topic=selected_topic,
                        limit=10
                    )
                if documents:
                    # Create a DataFrame from search results
                    df_search_results = pd.DataFrame(documents)

                    # Select and reorder columns as desired
                    desired_columns = ['file_name', 'topic', 'sub_topic', 'file_type', 'sha256', 'fuzzy_hash', 'text']
                    df_search_results = df_search_results[desired_columns]

                    # Rename columns for better readability
                    df_search_results.rename(columns={
                        'file_name': 'File Name',
                        'topic': 'Main Topic',
                        'sub_topic': 'Subtopic',
                        'file_type': 'File Type',
                        'sha256': 'SHA-256 Hash',
                        'fuzzy_hash': 'Fuzzy Hash',
                        'text': 'Content Preview'
                    }, inplace=True)

                    # Create a content preview by truncating the text
                    df_search_results['Content Preview'] = df_search_results['Content Preview'].apply(
                        lambda x: x[:500] + '...' if len(x) > 500 else x
                    )

                    # Display the search results table
                    st.write(f"**Found {len(documents)} documents in topic '{selected_topic}':**")
                    st.dataframe(df_search_results)

                    # Optionally, add export functionality for search results
                    if st.button("Export Search Results as CSV"):
                        try:
                            csv_search = df_search_results.to_csv(index=False)
                            st.download_button(
                                label="Download Search Results CSV",
                                data=csv_search,
                                file_name='search_results.csv',
                                mime='text/csv',
                            )
                            st.success("Search results exported successfully!")
                        except Exception as e:
                            st.error(f"Failed to export CSV: {e}")
                            logger.error(f"Failed to export CSV: {e}")
                else:
                    st.info(f"No documents found for topic '{selected_topic}'.")
        except Exception as e:
            st.error(f"Failed to search documents: {e}")
            logger.error(f"Failed to search documents: {e}")


# Run the main function
if __name__ == "__main__":
    main()

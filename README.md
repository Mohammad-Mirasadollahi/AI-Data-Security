# AI Data Security: Next-Gen Data Classification and Encryption

![License](https://img.shields.io/github/license/Mohammad-Mirasadollahi/AI-Data-Security)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Streamlit Version](https://img.shields.io/badge/streamlit-1.39.0-brightgreen)

## 📖 Description

**AI Data Security** is an **open-source** solution that leverages the power of **Artificial Intelligence (AI)** to automatically **classify** and **encrypt** your critical data, ensuring maximum protection. By replacing outdated methods like regex-based detection, it reduces errors, improves accuracy, and identifies both known and previously unknown sensitive information within your organization.

Designed as the ***last Line of Defense Against Adversaries***, AI Data Security guarantees that even if a breach occurs, your sensitive data remains completely inaccessible. Its intelligent algorithms eliminate manual intervention, streamline data protection processes, and ensure compliance with data protection laws.

With **AI Data Security**, you can confidently safeguard your data, future-proof your organization against evolving cyber threats.

Whether you're a researcher, student, or professional managing extensive documentation, this tool streamlines the
process of categorizing and searching through your documents with ease.
#
> ⚠️ **IMPORTANT DISCLAIMER**
>
> This project is currently a **Proof of Concept** and is under active development:
> - Features are incomplete and actively being developed
> - Bugs and breaking changes are expected
> - Project structure and APIs may change significantly
> - Documentation may be outdated or incomplete
> - Not recommended for production use at this time
> - Security features are still being implemented
>
> We welcome all feedback and contributions, but please use at your own risk!

## ✨ Features

- **Document Loading:** Supports loading various document types from a specified input folder.
- **Predefined Topic Assignment:** Assigns documents to user-defined topics using advanced NLP techniques.
- **Vector Embeddings:** Generates high-quality embeddings for each document to enable efficient similarity searches.
- **Database Integration:** Utilizes Qdrant to store document embeddings and metadata for scalable and fast retrieval.
- **User-Friendly UI:** Built with Streamlit, offering an intuitive interface for processing documents, viewing
  statistics, and searching.
- **Full Document View & Download:** Allows users to preview document content and download full documents directly from
  the UI.
- **Logging:** Comprehensive logging to track application events and errors for easy debugging.

## 📢 Feature Roadmap

### 🚀 Upcoming Features

- **Parallel Processing:** Improving performance with concurrent task execution.
- **Client Agent:** Installing agents on client machines for direct communication with the core system.
- **Data Encryption:** Protecting sensitive data with robust encryption.
- **OCR Capability:** Extracting text from images efficiently.
- **API Development:** Enabling seamless integration with external systems.

### 🌟 Long-term Vision

- **Advanced Admin Panel:** Centralized control and system monitoring.
- **File Logging:** Tracking file activity.
- **Ransomware Protection:** Securing data against Ransomwares.
- **2FA Security:** Adding an extra layer of authentication for file access.
- **GPU Utilization:** Accelerating processes with GPU power.
- **Multi-Language Support:** Making the system accessible globally.
- **Post-Quantum Cryptography:** Future-proofing data security with algorithms resistant to quantum computing threats.
- **System Clustering:** Boosting system reliability and optimizing processes by clustering resources, ensuring high availability and load balancing.

## 🛠️ Installation
Updating...
### Prerequisites

- **Python 3.8+**
- **Docker** (for running Qdrant)
- **Git**

### Steps

1. **Clone the Repository:**  
   Clone the project repository to your local machine using Git.

2. **Create a Virtual Environment:**  
   It's recommended to use a virtual environment to manage dependencies.

3. **Install Dependencies:**  
   Install the required Python packages listed in `requirements.txt`.

4. **Setup Qdrant:**  
   Run Qdrant using Docker to set up the vector database.

## 🔧 Configuration

### Environment Variables

Configure Qdrant and embedding model settings using environment variables in a `.env` file.

### YAML Configuration

Define predefined topics and folder paths in the `config.yaml` file.

Ensure that the input and output folders exist or can be created by the application, and verify that Qdrant is running
and accessible with the specified credentials.

## 🎯 Usage

1. **Run the Application:**  
   Launch the Streamlit app to access the user interface.

2. **Input Configuration:**
   - **Predefined Topics:** Enter each topic on a separate line.
   - **Input Folder Path:** Specify the directory containing your documents.
   - **Output Folder Path:** Specify where categorized documents will be stored.
   - Start processing to categorize your documents.

3. **View Database Statistics:**  
   Access statistics about the total number of documents and their distribution across topics.

4. **Search Documents:**  
   Select a topic and enter a query to search for similar documents. View previews and download full documents as
   needed.

## 📂 Project Structure

```
AI-Data-Security/
│
├── app.py
├── main.py
├── config.py
├── config.yaml
├── requirements.txt
├── README.md
├── .env
├── logs/
│   └── document_loader.log
├── input_documents/
│   └── ... (Your input documents)
├── output_documents/
│   └── ... (Categorized documents)
├── DatabaseHandler/
│   └── database_handler.py
├── DocumentLoader/
│   └── document_loader.py
└── TopicModeler/
    └── topic_modeler.py
```

- **app.py:** Streamlit application handling the user interface.
- **main.py:** Core processing functions for document handling and categorization.
- **config.py:** Configuration settings for paths and Qdrant credentials.
- **config.yaml:** YAML configuration file for predefined topics and folder paths.
- **.env:** Environment variables for Qdrant configuration and embedding model.
- **requirements.txt:** Python dependencies required for the project.
- **DatabaseHandler/database_handler.py:** Handles interactions with the Qdrant vector database.
- **DocumentLoader/document_loader.py:** Loads documents from the input folder.
- **TopicModeler/topic_modeler.py:** Assigns topics to documents and generates embeddings.
- **logs/:** Directory containing log files for tracking events and errors.
- **input_documents/:** Directory where you place documents to be processed.
- **output_documents/:** Directory where categorized documents are stored.

---

**Happy Document Categorizing! 🚀**

If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
Your feedback is invaluable!


---
## Installation Guide
#### _updating..._
### 1. Clone the Repository

Clone the project repository to your local machine using Git:

```bash
git clone https://github.com/Mohammad-Mirasadollahi/AI-Data-Security.git
```

### 2. Navigate to the Project Directory

Change into the project directory:

```bash
cd AI-Data-Security
```

### 3. Run the Installation Script

Execute the `install.sh` script to set up the environment and install all necessary dependencies:

```bash
source install.sh
```

> **Note:** If you encounter a permission error, make the script executable first:

```bash
chmod +x install.sh
source install.sh
```

### 4. Run the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

Access the application via the URL provided in the terminal, typically [http://localhost:8501](http://localhost:8501).

---

# API Documentation
Updating...

## Running the API

Start the FastAPI server using Uvicorn:

```bash
uvicorn api:app --reload
```

- **Server URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Endpoints

### 1. Health Check

- **Method:** `GET`
- **URL:** `/healthcheck`
- **Description:** Check if the API is running.

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/healthcheck
```

**Response:**
```json
{
  "status": "ok",
  "message": "API is running."
}
```

---

### 2. Process Documents with Predefined Topics

- **Method:** `POST`
- **URL:** `/process/predefined`
- **Description:** Categorize documents using predefined topics.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/process/predefined \
  -H "Content-Type: application/json" \
  -d '{
        "predefined_topics": {
          "Technology": ["AI", "Blockchain"],
          "Finance": ["Investing", "Banking"]
        },
        "input_folder": "/path/to/input",
        "output_folder": "/path/to/output"
      }'
```

**Response:**
```json
{
  "message": "Documents processed with predefined topics successfully."
}
```

---

### 3. Process Documents with Automatic Topics

- **Method:** `POST`
- **URL:** `/process/auto`
- **Description:** Categorize documents using automatic topic modeling.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/process/auto \
  -H "Content-Type: application/json" \
  -d '{
        "input_folder": "/path/to/input",
        "output_folder": "/path/to/output"
      }'
```

**Response:**
```json
{
  "message": "Documents processed with automatic topics successfully."
}
```

---

### 4. Get Database Statistics

- **Method:** `GET`
- **URL:** `/statistics`
- **Description:** Retrieve document statistics.

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/statistics
```

---

### 5. Get All Documents

- **Method:** `GET`
- **URL:** `/documents`
- **Description:** Retrieve all stored documents.

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/documents
```
---


Feel free to customize and expand upon this README as your project evolves. Good luck with your open-source journey!

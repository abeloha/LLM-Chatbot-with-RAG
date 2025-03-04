# AI Chatbot for Automating Customer Service

## Overview

This project is a prototype AI chatbot designed to automate customer service interactions for businesses. It leverages Retrieval-Augmented Generation (RAG) to improve response accuracy by combining Large Language Models (LLMs) with vector-based document retrieval.

## Features

- **Conversational AI**: Uses an LLM to generate human-like responses.
- **Retrieval-Augmented Generation (RAG)**: Fetches relevant data before responding to user queries.
- **Streamlit UI**: Provides an interactive web interface.
- **Vector Search with ChromaDB**: Stores and retrieves relevant documents efficiently.
- **MySQL Storage**: Saves user interactions for analytics and improvements.

## Technology Stack

### **1. Programming Language**

- Python

### **2. User Interface**

- Streamlit

### **3. Vector Database**

- ChromaDB

### **4. Structured Database**

- MySQL

### **5. Python Libraries**

- `langchain`
- `torch`
- `transformers`
- `sentence-transformers`
- `datasets`
- `faiss-cpu`
- `groq`
- `langchain_chroma`
- `langchain_community`
- `langchain_text_splitters`
- `mysql_connector_repackaged`
- `python-dotenv`
- `streamlit`
- `pypdf`

## Installation

As always recomended,  set up your virtual enviroment and install the required dependencies:
```sh
pip install langchain torch transformers sentence-transformers datasets faiss-cpu \
    groq langchain_chroma langchain_community langchain_text_splitters \
    mysql_connector_repackaged python-dotenv streamlit pypdf
```

## Project Structure

```
.
├── chatbot.py            # Main chatbot script
├── load_vector_db.py     # Script to load documents into vector database
├── requirements.txt      # Required dependencies
├── .env                  # Environment variables (API keys, database credentials)
├── data/                 # Folder containing source documents (PDFs)
├── chroma_db/            # Folder for ChromaDB persistence
└── README.md             # Project documentation
```

## Usage

### **1. Load Data into Vector Database**
Put your PDFs in the `data/` folder.
Run the following command to process and store documents in ChromaDB:

```sh
python load_vector_db.py
```

### **2. Start the Chatbot**

```sh
streamlit run app.py
```

## Key Functionalities

### **1. Data Ingestion (`load_vector_db.py`)**

- Extracts text from PDFs.
- Splits documents into chunks.
- Stores them in ChromaDB.

### **2. Chatbot Interaction (`chatbot.py`)**

- Retrieves relevant documents.
- Uses an LLM to generate responses.
- Maintains conversation context.

## Enhancements Implemented

- **Smart Context Retention**: Keeps track of past interactions.
- **Term Boosting**: Improves search results by emphasizing key terms.
- **Follow-Up Detection**: Identifies follow-up questions for better responses.

## Environment Variables (`.streamlit/secrets.toml` file)

```ini
APP_NAME="Your Chatbot Name"
WEBSITE="https://yourwebsite.com"
DATABASE_URL="mysql://user:password@host/dbname"
GROQ_API_KEY="your-groq-api-key"
# Database Configuration
DB_HOST = "localhost"
DB_USER = "user"
DB_PASSWORD = "password"
DB_NAME = "db"
```

## Future Improvements

- Add authentication for user tracking.
- Improve UI for better user experience.
- Implement multi-language support.

## License

You are free to use, modify, and distribute this project under the terms of the MIT License.

---
For any questions, contact me at abonuoha@gmail.com or https://www.linkedin.com/in/abeloha/.

# UniBot: Intelligent Study Assistant

UniBot is a hybrid application designed to assist students by processing documents (PDF/TXT) and answering questions based on their content using Retrieval-Augmented Generation (RAG).

<!--The project consists of two distinct parts:
-->
- **AI Engine (Python):** A backend API powered by FastAPI, LangChain, and Llama 3 (via Groq), with a frontend interface built in Streamlit.
<!--- **Web Portal (.NET/Umbraco):** A robust Content Management System to manage the broader educational platform.
-->
---

## Project Structure

The repository is organized as the following:

```plaintext
UniBotProject/
├── aiEngine/                  # Python AI Logic
│   ├── db_unibot/             # Persistent Vector Database (ChromaDB)
│   ├── setupDependencies/     # Installation scripts
│   │   ├── requirements.txt   # Python dependencies
│   │   └── setup.sh           # Environment setup script
│   ├── uploads/               # Temporary storage for uploaded files
│   ├── .env                   # Environment variables (API Keys)
│   ├── gui.py                 # Streamlit Frontend (User Interface)
│   └── main.py                # FastAPI Backend (RAG Engine)
├── unibot-venv/               # Python Virtual Environment
├── run.sh                     # Master Orchestration Script
└── README.md                  # Project Documentation
```

## Technology Stack
### AI Engine

- **LLM:** Llama 3.3 70b Versatile (via Groq API)
- **Framework:** FastAPI (Backend API)
- **Interface:** Streamlit (Chat UI)
- **Orchestration:** LangChain (Chains, History, Prompts)
- **Vector Database:** ChromaDB (Local persistence)
- **Embeddings:** HuggingFace (all-MiniLM-L6-v2)
- **Processing:** PyPDF (PDF Parsing)

## Prerequisites

Before running the project, ensure you have the following installed:
- **Python 3.10+**
- **Git**
- **Groq API Key** (free key from Groq Console)

## Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/your-username/UniBotProject.git
cd UniBotProject
```

### 2. Configure Environment Variables

Create a .env file inside the aiEngine folder.

```bash
cd aiEngine
```

```plaintext
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### 3. Run the Automated Setup

From the project root:
```bash
chmod +x aiEngine/setupDependencies/setup.sh
./aiEngine/setupDependencies/setup.sh
```

#### What this script does:
- Locates the project root
- Creates the virtual environment `unibot-venv`
- Activates the environment
- Installs all dependencies from `requirements.txt`

## Running the Application
### 1. Make the runner executable
```bash
chmod +x run.sh
```

### 2. Start all services
```bash
./run.sh
```

### 3. Access the Services
- AI Backend (Swagger): http://localhost:8000/docs
- Chat Interface: http://localhost:8501
**To stop:** Press `Ctrl + C`. All background services will be terminated automatically.

## Code Deep Dive
### 1. `aiEngine/main.py` — The Brain
- Loads environment variables and persistent paths
- Initializes `ChatGroq` with `llama-3.3-70b-versatile`
- Uses low temperature (0.1) for factual accuracy

### `/upload`
- Accepts PDF or TXT files
- Uses `PyPDFLoader` or `TextLoader`
- Splits text with `RecursiveCharacterTextSplitter`
- Stores vectors in ChromaDB

### `/ask`
- Retrieves top `k=3` relevant chunks
- Maintains chat memory via `RunnableWithMessageHistory`
- Enforces citation format (`filename.pdf`)
- Answers in Pt-Pt or English

### 2. `aiEngine/gui.py` — The Interface
- Streamlit-based frontend
- Unique UUID per user session
- Sidebar for document upload
- Chat UI with persistent history
- Displays AI answers and cited sources

### 3. `run.sh` — The Orchestrator
- Activates the virtual environment
- Runs FastAPI and Streamlit in background <!-- and Umbraco -->
- Handles `SIGINT` to clean up all processes

## API Documentation
### `POST /upload`
Uploads a document. **Body:** `form-data` -> `file`: binary

**Response**
```json
{
"status": "success",
"message": "lecture_notes.pdf uploaded"
}
```
<br>

### `GET /ask`
Ask a question. **Query Parameters:**`question`, `session_id`

**Response**
```json
{
"question": "What is photosynthesis?",
"answer": "Photosynthesis is the process...",
"sources": ["biology_chapter1.pdf"],
"session_id": "user-123"
}
```

## Future Roadmap
- Reranking for improved retrieval
- Persistent chat memory (SQLite)
- Follow-up question suggestions
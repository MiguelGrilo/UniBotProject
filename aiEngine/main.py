import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List

# https://docs.langchain.com/
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader#, UnstructuredFileLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.documents import Document

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="UniBot Project")

# GLOBAL CONFIGS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "db_unibot")
UPLOAD_DIR = os.path.join(SCRIPT_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Model Configuration (LLM)
# No need to use GROQ_API_KEY as an argument, it loads automatically
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
)

# Embeddings Configuration
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Low-dimensional, dense vector representations of high-dimensional data that captures
# semantic meaning and relationships between words in this case (Somewhat like a KMeans
# after transforming data in number vectors

# Dictionary to store session history, enabling short term memory
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Vectors database
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)


# ENDPOINTS


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Temp Files for Langchain to read
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Loader selection
        # File will be transformed in 'documents' object type
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        elif file.filename.endswith(".txt"):
            loader = TextLoader(temp_path, encoding="utf-8")
        # elif file.filename.endswith((".docx", ".doc", ".pptx", ".ppt", ".md", ".markdown")):
        #     loader = UnstructuredFileLoader(temp_path)
        else:
            os.remove(temp_path)
            return {"status": "error", "message": "Format not supported"}

        documents = loader.load()

        # Splitter
        # Data fragmentation to help AI not get lost in the proccess
        # Data will be divided in chunks of 1000 characters with overlap on 100 to not lose
        # context between chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)

        # Create Database
        Chroma.from_documents(
            documents=texts,
            # HuggingFace model transforms text in vectors and stores them in disk so AI can search for meanings
            embedding=embeddings,
            persist_directory=DB_PATH
        )

        os.remove(temp_path)
        return {"status": "success", "message": f"{file.filename} uploaded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask")
async def ask_question(question: str, session_id: str = "default"):
    try:
        # Retriever Configuration
        # The retriever looks for the 3 most similar text charts
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})

        # Extract sources
        # Saves original sources to be mentioned in the future
        context_docs = retriever.invoke(question)

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        formatted_context = format_docs(context_docs)

        # Define default prompt in memory
        system_prompt = (
            "Usa os seguintes pedaços de contexto recuperado para responder à pergunta. "
            "Se não souberes a resposta, diz que não sabes. Usa um tom amigável e conciso em Português de Portugal ou Inglês, conforme o idioma do último prompt."
            "Sempre que usares informação de um documento, cita o nome do ficheiro entre parênteses no final da frase.\n\n"
            "{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"), # Takes in consideration previous session history
            ("human", "{question}")
        ])

        # Generation chain
        chain = (
            # Gathers the system prompt and the context
            prompt
            # Llama 3 (Groq) gets all the info it needs and generates the final answer
            | llm
        )

        # Adds memory to the chain
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history",
        )

        # Execute
        # Use the context manually formated
        response = chain_with_history.invoke(
            {"question": question, "context": formatted_context},
            config={"configurable": {"session_id": session_id}}
        )

        # Proccess sources
        # Extract filenames
        sources = [doc.metadata.get("source", "Unknown") for doc in context_docs]
        # Clean temp sources
        clean_sources = list(set([os.path.basename(s).replace("temp_", "") for s in sources]))

        # Answer return format
        return {
            "question": question,
            "answer": response.content,
            "sources": clean_sources,
            "session_id": session_id
        }

    except Exception as e:
        print(f"Error: {str(e)}") # Log para debug no terminal
        raise HTTPException(status_code=500, detail=str(e))

# RUN: uvicorn main:app --reload &

# Future implementations:
# - Reranking (Otimização da Resposta)
# - Sugestão de Perguntas (Follow-up Questions)
# - Gestão de Memória Persistente (SQL)
# DocuMind AI 

DocuMind is an open-source, enterprise-grade AI knowledge base. It allows you to upload business documents and chat with them in real-time. Built entirely from scratch using the modern Python ecosystem and raw SQL/pgvector, avoiding heavy abstraction frameworks like LangChain for ultimate performance and control.

## 🚀 Features

- **Retrieval-Augmented Generation (RAG):** Answers questions based strictly on the uploaded documents.
- **FastAPI Backend:** Blazing fast asynchronous backend.
- **Vite + React Frontend:** A beautiful, responsive, glassmorphic UI.
- **Real-Time Streaming:** Streams the AI's response using Server-Sent Events (SSE) with a typing indicator.
- **Sliding Window Memory:** Remembers the last 5 messages of context for follow-up questions.
- **Multi-tenant Architecture:** Documents and chats are securely separated by Organization and User.
- **Vector Database:** Uses PostgreSQL with `pgvector` for scalable cosine similarity search.

## 🏗️ Architecture

```mermaid
graph TD
    User([User]) -->|HTTP / SSE| Frontend[React + Vite UI]
    Frontend -->|REST API| Backend[FastAPI Server]
    Backend -->|SQL| DB[(PostgreSQL + pgvector)]
    Backend -->|Gemini API| LLM[Google Gemini 2.5 Flash]

    subgraph Document Processing Pipeline
        Backend --> Extractor[Text Extractor]
        Extractor --> Chunker[Text Chunker]
        Chunker --> Embedder[Gemini Embeddings]
        Embedder --> DB
    end
```

## 🛠️ Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Alembic, Uvicorn, Google Gemini SDK
- **Frontend:** React 18, Vite, React Router
- **Database:** PostgreSQL 16, pgvector
- **Deployment:** Docker, Docker Compose, Render (Infrastructure as Code)

## 🏁 Getting Started (Local Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- A Google Gemini API Key

### 1. Database Setup
Start the PostgreSQL database with the pgvector extension:
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
pip install -r requirements.txt

# Run migrations to create tables
alembic upgrade head

# Start the server
uvicorn main:app --reload
```
Make sure you have a `.env` file in the `backend` directory containing:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/documind
JWT_SECRET_KEY=your_super_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:5173.

## 📦 Production Deployment

This project includes a production `docker-compose.prod.yml` and a `render.yaml` blueprint for one-click deployment to [Render](https://render.com).

### Deploying via Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
This will build and run the database, backend, and frontend behind Nginx.

## 📜 License
MIT License

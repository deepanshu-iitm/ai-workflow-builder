# 🚀 AI Workflow Builder

A **No-Code/Low-Code** web application that enables users to visually create and interact with intelligent AI workflows. Build powerful RAG (Retrieval-Augmented Generation) pipelines by connecting components through an intuitive drag-and-drop interface.


## ✨ Features

- **Visual Workflow Builder**: Drag-and-drop interface using React Flow
- **Knowledge Base (RAG)**: Upload PDFs and create searchable knowledge bases with ChromaDB
- **LLM Integration**: Powered by Google Gemini for intelligent responses
- **Web Search**: Real-time web search capability via SerpAPI
- **Chat Interface**: Interactive chat to query your workflows
- **Workflow Validation**: Automatic validation before execution
- **Modular Components**: 4 core components that can be connected in various ways

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Sidebar   │  │   Canvas    │  │   Config    │              │
│  │ (Components)│  │ (React Flow)│  │   Panel     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                         │                                        │
│  ┌──────────────────────┴──────────────────────────┐            │
│  │              Chat Modal (AI Interaction)         │            │
│  └──────────────────────────────────────────────────┘            │
└────────────────────────────│─────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼─────────────────────────────────────┐
│                      Backend (FastAPI)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Document   │  │  Workflow   │  │    Chat     │              │
│  │   Service   │  │   Engine    │  │   Service   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐              │
│  │  ChromaDB   │  │   Gemini    │  │  SerpAPI    │              │
│  │(Vector Store)│  │    LLM     │  │ (Web Search)│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└────────────────────────────│─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      PostgreSQL Database                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Documents  │  │  Workflows  │  │    Chat     │              │
│  │  Metadata   │  │   & Nodes   │  │   History   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└──────────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. User Query (Input)
- Entry point for user queries
- Accepts natural language input
- Passes queries to connected components

### 2. Knowledge Base
- Upload and process PDF documents
- Extracts text using PyMuPDF
- Generates embeddings with Gemini
- Stores vectors in ChromaDB
- Retrieves relevant context for queries

### 3. LLM Engine
- Powered by Google Gemini (Flash/Pro)
- Configurable temperature and max tokens
- Custom system prompts
- Optional web search integration

### 4. Output
- Displays final AI responses
- Supports Markdown rendering
- Shows execution metadata

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, React Flow, Zustand |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 15 |
| Vector Store | ChromaDB |
| LLM | Google Gemini |
| Embeddings | Gemini Embedding Model |
| Web Search | SerpAPI |
| PDF Processing | PyMuPDF |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (optional) |

## 📦 Project Structure

```
ai-workflow-builder/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── nodes/           # React Flow node components
│   │   ├── store/           # Zustand state management
│   │   ├── api/             # API client
│   │   └── types/           # TypeScript types
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Configuration
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   └── requirements.txt
├── docker/                   # Docker configurations
├── k8s/                      # Kubernetes manifests
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+ (or Docker)
- Google Gemini API Key
- SerpAPI Key (optional, for web search)

### 1. Clone the Repository

```bash
git clone https://github.com/deepanshu-iitm/ai-workflow-builder.git
cd ai-workflow-builder
```

### 2. Setup Environment Variables

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://workflow_user:workflow_pass@localhost:5432/workflow_db
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

### 3. Start PostgreSQL (using Docker)

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 6. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs


## 📖 API Documentation

### Documents API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload a document |
| GET | `/api/documents/` | List all documents |
| GET | `/api/documents/{id}` | Get document details |
| DELETE | `/api/documents/{id}` | Delete a document |

### Workflows API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workflows/` | Create a workflow |
| GET | `/api/workflows/` | List workflows |
| GET | `/api/workflows/{id}` | Get workflow |
| PUT | `/api/workflows/{id}` | Update workflow |
| POST | `/api/workflows/validate` | Validate workflow |

### Chat API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/query` | Execute a query |
| POST | `/api/chat/sessions` | Create chat session |
| GET | `/api/chat/sessions` | List sessions |
| GET | `/api/chat/sessions/{id}` | Get session with messages |



## 🎯 Usage Guide

### Building a Workflow

1. **Add Input Node**: Drag the "Input" component to the canvas
2. **Add Knowledge Base** (optional): Upload documents and configure retrieval
3. **Add LLM Engine**: Configure the AI model and prompts
4. **Add Output Node**: Connect to display results
5. **Connect Nodes**: Draw lines between node handles
6. **Build Stack**: Click "Build Stack" to validate
7. **Chat**: Click "Chat With AI" to interact

### Example Workflow

```
[Input] → [Knowledge Base] → [LLM Engine] → [Output]
```

This creates a RAG pipeline that:
1. Accepts user questions
2. Retrieves relevant document context
3. Generates AI-powered answers
4. Displays the response



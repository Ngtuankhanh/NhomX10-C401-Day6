# my-agent-app

A production-ready fullstack monorepo for an AI agent application.

## Monorepo Structure

```
my-agent-app/
├── frontend/       ← Next.js chat UI (create-agent-chat-app)
├── backend/        ← Python FastAPI + LangGraph agent
├── .gitignore
└── README.md
```

## Quick Start

### 1. Backend (FastAPI + LangGraph)

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload --port 2024
```

### 2. Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (already done at scaffold time)
# NEXT_PUBLIC_API_URL=http://localhost:2024
# NEXT_PUBLIC_ASSISTANT_ID=agent

# Run the dev server
npm run dev
```

The frontend will be available at **http://localhost:3000** and will communicate with the backend at **http://localhost:2024**.

## API Endpoints

| Method | Path             | Description              |
|--------|------------------|--------------------------|
| GET    | `/health`        | Health check             |
| POST   | `/agent/invoke`  | Invoke the LangGraph agent |

### POST `/agent/invoke`

**Request:**
```json
{ "input": "What is the weather in Hanoi?" }
```

**Response:**
```json
{ "output": "..." }
```

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | Next.js, React, TypeScript        |
| Backend  | FastAPI, LangGraph, LangChain     |
| LLM      | OpenAI GPT-4o (via `ChatOpenAI`)  |
| Agent    | ReAct agent via `create_react_agent` |

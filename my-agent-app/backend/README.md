# Backend — FastAPI + LangGraph Agent

A Python backend exposing a LangGraph ReAct agent via FastAPI.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in your OPENAI_API_KEY in .env
```

## Running

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 2024
```

## Endpoints

- `GET  /health`         → `{"status": "ok"}`
- `POST /agent/invoke`   → `{"input": "..."}` → `{"output": "..."}`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py   ← package marker
│   ├── config.py     ← pydantic-settings configuration
│   ├── graph.py      ← LangGraph create_react_agent setup
│   └── main.py       ← FastAPI app with CORS + routes
├── .env.example
├── requirements.txt
└── README.md
```

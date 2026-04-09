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

- `GET  /health`
- `POST /api/chat/session`
- `POST /api/chat/message`
- `GET  /api/evals/traces/{trace_id}`
- `GET  /api/evals/sessions/{session_id}/latest-trace`
- `POST /api/evals/judge`

## Demo Observability

Structured request traces are written to:

```bash
backend/runtime/ai_request_traces.jsonl
```

Judge results are written to:

```bash
backend/runtime/ai_judge_results.jsonl
```

See the audit and rollout notes in:

```bash
backend/docs/ai-eval-audit.md
```

## Project Structure

```
backend/
├── app/
│   ├── config.py         ← pydantic-settings configuration
│   ├── main.py           ← FastAPI app with CORS + routes
│   ├── observability/    ← structured trace + judge schemas/store
│   └── presentation/     ← chat + eval API routers
├── docs/
│   └── ai-eval-audit.md
├── .env.example
├── requirements.txt
└── README.md
```

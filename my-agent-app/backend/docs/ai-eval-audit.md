# AI Evaluation Audit

## 1. Current Request Lifecycle

Current flow before the patch:

1. `POST /api/chat/message` enters `app/presentation/api/chat_router.py`.
2. `AgentAService.send_user_message()` stores the user message in session state via `app/application/use_cases/chat_handler.py`.
3. `run_agent()` invokes the LangGraph ReAct graph in `app/infrastructure/ai_services/agents/agent.py`.
4. Agent A can call:
   - `specialist_agent_tool()` in `app/infrastructure/ai_services/agents/specialist_agent.py`
   - booking/data tools in `app/infrastructure/ai_services/tools/booking_tools.py`
5. The final assistant text is returned to `AgentAService`, then persisted into the in-memory session repo and returned to the frontend.

## 2. Audit Findings

### Logging coverage before the patch

Missing or not persisted in any structured form:

- `raw_prompt`
- `system_prompt_version`
- `model_completion`
- `latency`
- `token_usage`
- `tool_calls`

Only `session_id` was carried through the request path, but not attached to an execution trace object.

### Context loss risks before the patch

- `run_agent()` collapsed the entire LangGraph execution into a single string, so intermediate model/tool evidence was discarded.
- Specialist Agent model calls were invisible to the outer system.
- Errors were only printed with `print(...)`, so failed runs had no structured replay artifact for evaluation.
- Session state lived only in `MemorySessionRepository`, so restart = lost history and lost audit context.

### Performance risks before the patch

- `async` FastAPI routes called synchronous LangGraph and `requests` code directly, so the event loop could be blocked during long model/tool calls.
- If synchronous file logging were added naively in the same path, p95 latency would worsen further.

## 3. Implemented Demo-Grade Fix

### Structured trace

Added:

- `app/observability/schemas.py`
- `app/observability/trace_runtime.py`
- `app/observability/trace_store.py`

Each AI request now writes a JSONL trace with:

- `trace_id`
- `session_id`
- `raw_prompt`
- `system_prompt_version`
- `system_prompt_versions_seen`
- `model_completion`
- `final_output`
- `latency_ms`
- `token_usage`
- `model_calls`
- `tool_calls`
- `errors`

Output location:

- `backend/runtime/ai_request_traces.jsonl`

### Non-blocking logging

The demo logger uses a background thread + queue and writes JSONL asynchronously, so file I/O is decoupled from the response path.

### Event-loop protection

Chat and judge routes now use `run_in_threadpool(...)`, which prevents the FastAPI event loop from being blocked by sync LangGraph/tool work.

## 4. LLM-as-a-Judge Design

### Static schema

Judge schema lives in `app/observability/schemas.py`.

Core metrics:

- `grounding_factuality`
- `constraint_compliance`
- `instruction_following`

Each metric returns:

- `score` from 1 to 5
- `passed`
- `rationale`
- `evidence`

Final result also includes:

- `insufficient_reference_data`
- `blocking_issues`
- `improvement_actions`
- `overall_score`
- `overall_verdict`

### Judge prompt strategy

Judge prompt lives in `app/infrastructure/ai_services/agents/prompts.py`.

Guardrails:

- Judge must only use `candidate_output`, `raw_prompt`, `tool_calls`, and `reference_data`.
- Judge must not invent ground truth.
- Missing or weak reference data must explicitly trigger `insufficient_reference_data = true`.
- Overall verdict is computed deterministically in code to reduce prompt drift.

### Reference data contract

Judge input requires explicit `reference_data`:

- `ground_truth_facts`
- `required_constraints`
- `required_output_format`
- `expected_answer`
- `forbidden_claims`
- `task_success_criteria`

This prevents a “vibe-based” judge that grades without a target.

## 5. Demo API

### Get latest trace for a session

`GET /api/evals/sessions/{session_id}/latest-trace`

### Get a specific trace

`GET /api/evals/traces/{trace_id}`

### Run judge

`POST /api/evals/judge`

Example body:

```json
{
  "trace_id": "TRACE_ID_HERE",
  "reference_data": {
    "ground_truth_facts": [
      "User asked for a specialty suggestion based on headache symptoms."
    ],
    "required_constraints": [
      "Do not prescribe medication.",
      "Do not claim a definitive diagnosis."
    ],
    "task_success_criteria": [
      "Suggest a plausible specialty.",
      "Keep the answer within Vinmec assistant scope."
    ]
  }
}
```

## 6. Remaining Demo Limits

- Trace data is file-based JSONL, not durable queue storage.
- Session persistence is still in-memory.
- Raw prompt/tool payloads may contain PII, so production rollout needs redaction and retention controls.
- Judge quality still depends on the quality of `reference_data`; no reference means weaker factual scoring by design.

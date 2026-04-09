from __future__ import annotations

import json
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from typing import Any

from app.observability.schemas import AgentRequestTrace, JudgeEvaluationResult


class AsyncJsonlTraceStore:
    """Very small async JSONL store for demo-grade observability."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.base_dir / "ai_request_traces.jsonl"
        self.judge_path = self.base_dir / "ai_judge_results.jsonl"
        self._queue: Queue[tuple[Path | None, str | None]] = Queue()
        self._stop_event = Event()
        self._worker = Thread(target=self._drain_queue, name="trace-jsonl-writer", daemon=True)
        self._worker.start()

    def append_trace(self, trace: AgentRequestTrace) -> None:
        self._enqueue(self.trace_path, trace.model_dump_json())

    def append_judge_result(self, result: JudgeEvaluationResult) -> None:
        self._enqueue(self.judge_path, result.model_dump_json())

    def get_trace(self, trace_id: str) -> AgentRequestTrace | None:
        return self._read_last_match(
            self.trace_path,
            predicate=lambda payload: payload.get("trace_id") == trace_id,
            model_cls=AgentRequestTrace,
        )

    def latest_trace_for_session(self, session_id: str) -> AgentRequestTrace | None:
        return self._read_last_match(
            self.trace_path,
            predicate=lambda payload: payload.get("session_id") == session_id,
            model_cls=AgentRequestTrace,
        )

    def close(self) -> None:
        if self._stop_event.is_set():
            return
        self._queue.join()
        self._stop_event.set()
        self._queue.put((None, None))
        self._worker.join(timeout=2)

    def _enqueue(self, path: Path, payload: str) -> None:
        self._queue.put((path, payload))

    def _drain_queue(self) -> None:
        while True:
            path, payload = self._queue.get()
            try:
                if path is None or payload is None:
                    return
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(payload)
                    handle.write("\n")
            finally:
                self._queue.task_done()

    def _read_last_match(
        self,
        path: Path,
        predicate: Any,
        model_cls: type[AgentRequestTrace],
    ) -> AgentRequestTrace | None:
        if not path.exists():
            return None

        match: AgentRequestTrace | None = None
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                payload = json.loads(stripped)
                if predicate(payload):
                    match = model_cls.model_validate(payload)
        return match

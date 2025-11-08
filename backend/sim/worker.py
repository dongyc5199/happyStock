"""Async worker utilities for simulation tick processing."""
from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from typing import Any, Dict

from .schemas import TickRequest
from .services import SimulationService


class SimulationWorker:
    """Background worker that consumes tick requests via asyncio.Queue."""

    def __init__(
        self,
        service: SimulationService,
        *,
        max_queue_size: int = 256,
        retry_attempts: int = 3,
        retry_delay: float = 0.5,
    ) -> None:
        self._service = service
        self._queues: Dict[int, asyncio.Queue[TickRequest]] = defaultdict(asyncio.Queue)
        self._tasks: Dict[int, asyncio.Task[Any]] = {}
        self._lock = asyncio.Lock()
        self._active_sessions: set[int] = set()
        self._max_queue_size = max_queue_size
        self._retry_attempts = retry_attempts
        self._retry_delay = retry_delay

    async def start(self, session_id: int) -> None:
        async with self._lock:
            if session_id in self._tasks:
                return
            queue = self._queues[session_id]
            self._tasks[session_id] = asyncio.create_task(self._run(session_id, queue))
            self._active_sessions.add(session_id)

    async def stop(self, session_id: int) -> None:
        async with self._lock:
            task = self._tasks.pop(session_id, None)
            if task:
                task.cancel()
            self._queues.pop(session_id, None)
            self._active_sessions.discard(session_id)
        if task:
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def submit(self, request: TickRequest) -> None:
        queue = self._queues[request.session_id]
        if queue.qsize() >= self._max_queue_size:
            raise RuntimeError("simulation queue at capacity")
        await queue.put(request)

    async def _run(self, session_id: int, queue: asyncio.Queue[TickRequest]) -> None:
        while True:
            request = await queue.get()
            try:
                await self._process_with_retry(request)
            finally:
                queue.task_done()

    async def _process_with_retry(self, request: TickRequest) -> None:
        attempt = 0
        while True:
            try:
                await self._service.process_tick(
                    session_id=request.session_id,
                    session_code=request.session_code,
                    tick=request.tick,
                    orders=[order.model_dump() for order in request.orders],
                    timestamp=request.timestamp,
                )
                return
            except Exception as exc:  # pragma: no cover - defensive retry
                attempt += 1
                if attempt > self._retry_attempts:
                    print(
                        f"[!] SimulationWorker failed tick "
                        f"{request.session_code}:{request.tick} after {attempt} attempts: {exc}"
                    )
                    return
                await asyncio.sleep(self._retry_delay)


__all__ = ["SimulationWorker"]

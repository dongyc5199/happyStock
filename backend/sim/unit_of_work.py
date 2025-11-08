"""Unit of work helpers for the simulation backend."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

try:
    import asyncpg  # type: ignore
except ImportError:  # pragma: no cover
    asyncpg = None  # type: ignore[misc]


class SimulationUnitOfWork:
    """Simple unit-of-work wrapper around an asyncpg pool."""

    def __init__(self, pool: Any):
        self._pool = pool

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[Any]:
        if asyncpg is None:  # pragma: no cover
            raise RuntimeError("asyncpg 未安装，无法创建连接。")
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            async with conn.transaction():
                yield conn


async def create_pool(dsn: str, *, min_size: int | None = None, max_size: int | None = None) -> Any:
    """Create an asyncpg pool for the simulation database."""
    if asyncpg is None:  # pragma: no cover
        raise RuntimeError("asyncpg 未安装，无法创建连接池。")

    import os

    min_size = min_size if min_size is not None else int(os.getenv("SIM_DB_POOL_MIN", "2"))
    max_size = max_size if max_size is not None else int(os.getenv("SIM_DB_POOL_MAX", "10"))

    return await asyncpg.create_pool(dsn, min_size=min_size, max_size=max_size)

from __future__ import annotations

import asyncio
import sys
import unittest
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.agents import AgentRegistry, AgentStrategy, AgentContext, GeneratedOrder
from sim.cache import LeaderboardEntry
from sim.services import ImpactModel, SimulationService
from sim.types import (
    MarketSnapshot,
    OrderEventRecord,
    SimulationSession,
    TradeEventRecord,
)


@dataclass
class DummySessionRepo:
    created: List[SimulationSession] = field(default_factory=list)
    last_tick: Tuple[int, int] | None = None
    score_adjustments: list[tuple[int, float]] = field(default_factory=list)
    participants: dict[tuple[int, str], int] = field(default_factory=dict)
    _participant_seq: int = 0

    async def create_session(self, session: SimulationSession) -> SimulationSession:
        session.id = 1
        self.created.append(session)
        return session

    async def update_tick(self, session_id: int, tick: int) -> None:
        self.last_tick = (session_id, tick)

    async def adjust_participant_score(self, participant_id: int, delta: float) -> None:
        self.score_adjustments.append((participant_id, delta))

    async def ensure_participant(
        self,
        *,
        session_id: int,
        participant_code: str,
        participant_type: str,
        player_id: str | None = None,
        agent_profile_id: int | None = None,
    ) -> int:
        key = (session_id, participant_code)
        if key not in self.participants:
            self._participant_seq += 1
            self.participants[key] = self._participant_seq
        return self.participants[key]

    async def ensure_participants_bulk(
        self,
        *,
        session_id: int,
        payloads: Sequence[dict[str, Any]],
    ) -> dict[str, int]:
        result: dict[str, int] = {}
        for payload in payloads:
            code = payload["participant_code"]
            result[code] = await self.ensure_participant(
                session_id=session_id,
                participant_code=code,
                participant_type=payload.get("participant_type", "player"),
                player_id=payload.get("player_id"),
                agent_profile_id=payload.get("agent_profile_id"),
            )
        return result

    async def fetch_participant_ids(
        self, session_id: int, participant_codes: Sequence[str]
    ) -> dict[str, int]:
        result: dict[str, int] = {}
        for code in participant_codes:
            key = (session_id, code)
            if key in self.participants:
                result[code] = self.participants[key]
        return result


class DummyMarketRepo:
    def __init__(self) -> None:
        self.snapshots: list[MarketSnapshot] = []

    async def bulk_insert(self, snapshots: Iterable[MarketSnapshot]) -> None:
        self.snapshots.extend(snapshots)

    async def fetch_recent(self, session_id: int, limit: int) -> list[MarketSnapshot]:
        return list(self.snapshots)[:limit]


class DummyOrderRepo:
    def __init__(self) -> None:
        self.orders: list[OrderEventRecord] = []
        self.trades: list[TradeEventRecord] = []

    async def record_orders(self, events: Iterable[OrderEventRecord]) -> None:
        self.orders.extend(events)

    async def record_trades(self, trades: Iterable[TradeEventRecord]) -> None:
        self.trades.extend(trades)

    async def record_events(
        self,
        orders: Iterable[OrderEventRecord],
        trades: Iterable[TradeEventRecord],
    ) -> tuple[float, float]:
        await self.record_orders(orders)
        await self.record_trades(trades)
        return 0.0, 0.0


class DummyAgentLogRepo:
    def __init__(self) -> None:
        self.logs: list[Any] = []

    async def record_logs(self, logs: Iterable[Any]) -> None:
        self.logs.extend(logs)


class DummyCache:
    def __init__(self) -> None:
        self.entries: list[tuple[str, str, float]] = []
        self.leaderboard: list[LeaderboardEntry] = []
        self.scores: dict[str, float] = {}
        self.tick_updates: list[tuple[str, int]] = []
        self.coach_logs: list[dict[str, Any]] = []
        self.pool_stats: dict[str, dict[str, float]] = {}

    async def update_leaderboard(
        self, session: str, participant_id: str, score: float
    ) -> None:
        self.entries.append((session, participant_id, score))
        self.scores[participant_id] = score
        self._refresh_leaderboard()

    async def adjust_leaderboard(
        self, session: str, participant_id: str, delta: float
    ) -> None:
        self.entries.append((session, participant_id, delta))
        self.scores[participant_id] = self.scores.get(participant_id, 0.0) + delta
        self._refresh_leaderboard()

    async def publish_pool_stats(
        self,
        session: str,
        stats: dict[str, dict[str, float]],
        ttl_seconds: int = 5,
    ) -> None:
        self.pool_stats = stats

    async def top_leaderboard(
        self,
        session: str,
        limit: int = 10,
        reverse: bool = True,
    ) -> list[LeaderboardEntry]:
        return self.leaderboard[:limit]

    async def set_tick(self, session: str, tick: int) -> None:
        self.tick_updates.append((session, tick))

    async def enqueue_coach_log(self, payload: dict[str, Any], *, maxlen: int = 1000) -> None:  # noqa: ARG002
        self.coach_logs.append(payload)

    def _refresh_leaderboard(self) -> None:
        self.leaderboard = [
            LeaderboardEntry(participant_id=pid, score=score)
            for pid, score in sorted(
                self.scores.items(), key=lambda item: item[1], reverse=True
            )
        ]


class StubAgent(AgentStrategy):
    def __init__(self) -> None:
        super().__init__(code="stub")

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> list[GeneratedOrder]:
        return [
            GeneratedOrder(
                order_id=f"stub-order-{session_id}-{tick}",
                participant_id=f"agent-{session_id}",
                side="BUY",
                order_type="MARKET",
                quantity=5.0,
                price=None,
            )
        ]


class SimulationServiceTests(unittest.IsolatedAsyncioTestCase):
    async def _drain_background_tasks(self, service: SimulationService) -> None:
        while getattr(service, "_background_tasks", None):
            tasks = list(service._background_tasks)
            await asyncio.gather(*tasks)

    def _service(
        self,
    ) -> tuple[
        SimulationService,
        DummyMarketRepo,
        DummyOrderRepo,
        DummySessionRepo,
        DummyCache,
        DummyAgentLogRepo,
    ]:
        market_repo = DummyMarketRepo()
        order_repo = DummyOrderRepo()
        session_repo = DummySessionRepo()
        cache = DummyCache()
        agent_logs = DummyAgentLogRepo()
        service = SimulationService(
            session_repo=session_repo,
            market_repo=market_repo,
            order_repo=order_repo,
            cache=cache,
            agent_log_repo=agent_logs,
            impact_model=ImpactModel(alpha=0.5, beta=0.5, liquidity=1000.0),
            agents_enabled=True,
        )
        return service, market_repo, order_repo, session_repo, cache, agent_logs

    async def test_market_snapshot_delegation(self) -> None:
        service, market_repo, _, _, _, _ = self._service()
        snapshot = MarketSnapshot(
            session_id=1,
            tick=1,
            timestamp=datetime.now(timezone.utc),
            best_bid=100.0,
            best_ask=100.1,
            last_price=100.05,
            vwap_price=100.0,
            total_volume=500,
            imbalance=0.0,
            sentiment_score=0.0,
            liquidity_level=1.0,
            payload={},
        )

        await service.record_market_snapshots([snapshot])
        recent = await service.fetch_recent_market_state(session_id=1, limit=5)

        self.assertEqual(market_repo.snapshots, [snapshot])
        self.assertEqual(recent, [snapshot])

    async def test_leaderboard_workflow(self) -> None:
        service, _, _, _, _, _ = self._service()
        await service.update_leaderboard("session", "participant", 42.5)
        top = await service.top_leaderboard("session", limit=1)

        self.assertEqual(top[0].participant_id, "participant")
        self.assertEqual(top[0].score, 42.5)

    async def test_process_tick_persists_orders_and_trades(self) -> None:
        service, market_repo, order_repo, session_repo, cache, agent_logs = self._service()

        orders: Sequence[dict] = [
            {
                "order_id": "o1",
                "participant_id": "p1",
                "side": "SELL",
                "type": "LIMIT",
                "quantity": 10,
                "price": 100.0,
            },
            {
                "order_id": "o2",
                "participant_id": "p2",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 5,
            },
        ]

        result = await service.process_tick(
            session_id=1,
            session_code="s-001",
            tick=1,
            orders=orders,
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        await self._drain_background_tasks(service)

        self.assertEqual(len(order_repo.orders), 2)
        self.assertEqual(len(order_repo.trades), 1)
        self.assertEqual(order_repo.trades[0].price, 100.0)
        self.assertEqual(session_repo.last_tick, (1, 1))
        self.assertEqual(cache.tick_updates[-1], ("s-001", 1))
        self.assertGreater(cache.scores.get("p1", 0.0), 0.0)
        self.assertGreater(cache.scores.get("p2", 0.0), 0.0)
        self.assertTrue(agent_logs.logs)
        self.assertTrue(cache.coach_logs)
        self.assertEqual(result["status"], "accepted")
        self.assertTrue(result["trace_id"].startswith("s-001-"))
        self.assertTrue(all(evt.participant_db_id is not None for evt in order_repo.orders))
        self.assertTrue(
            all(trade.buyer_participant_db_id is not None for trade in order_repo.trades)
        )
        self.assertTrue(
            all(trade.seller_participant_db_id is not None for trade in order_repo.trades)
        )
        self.assertIn("snapshot", result)
        self.assertGreaterEqual(market_repo.snapshots[0].total_volume or 0, 5)

    async def test_coach_logs_include_recommendations(self) -> None:
        service, _, order_repo, _, cache, agent_logs = self._service()

        orders: Sequence[dict] = [
            {
                "order_id": "o11",
                "participant_id": "trader-b",
                "side": "SELL",
                "type": "LIMIT",
                "quantity": 4,
                "price": 99.5,
            },
            {
                "order_id": "o10",
                "participant_id": "trader-a",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 4,
            },
        ]

        await service.process_tick(
            session_id=2,
            session_code="session-coach",
            tick=2,
            orders=orders,
            timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
        )
        await self._drain_background_tasks(service)

        self.assertGreater(len(order_repo.trades), 0)
        self.assertGreater(len(agent_logs.logs), 0)
        self.assertGreater(len(cache.coach_logs), 0)
        first_log = agent_logs.logs[0]
        self.assertTrue(first_log.recommendations)
        queue_payload = cache.coach_logs[-1]
        self.assertIn("headline", queue_payload)
        self.assertEqual(queue_payload["session_code"], "session-coach")

    async def test_process_tick_merges_agent_orders(self) -> None:
        market_repo = DummyMarketRepo()
        order_repo = DummyOrderRepo()
        session_repo = DummySessionRepo()
        cache = DummyCache()
        agent_logs = DummyAgentLogRepo()
        registry = AgentRegistry()
        agent = StubAgent()
        await registry.register(session_id=1, agent=agent)

        service = SimulationService(
            session_repo=session_repo,
            market_repo=market_repo,
            order_repo=order_repo,
            cache=cache,
            agent_log_repo=agent_logs,
            agent_registry=registry,
            impact_model=ImpactModel(alpha=0.5, beta=0.5, liquidity=1000.0),
            agents_enabled=True,
        )

        player_order = {
            "order_id": "player-order-1",
            "participant_id": "player-1",
            "side": "SELL",
            "type": "LIMIT",
            "quantity": 5.0,
            "price": 100.0,
        }

        result = await service.process_tick(
            session_id=1,
            session_code="session-1",
            tick=1,
            orders=[player_order],
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        await self._drain_background_tasks(service)

        participant_ids = {event.participant_id for event in order_repo.orders}
        self.assertIn("agent-1", participant_ids)
        self.assertIn("player-1", participant_ids)

        self.assertTrue(
            any(trade.buyer_participant_id == "agent-1" for trade in order_repo.trades)
        )
        self.assertEqual(cache.scores.get("agent-1"), 5.0)
        self.assertEqual(result["orders"].count("stub-order-1-1"), 1)
        self.assertEqual(result["status"], "accepted")
        self.assertTrue(result["trace_id"].startswith("session-1-"))
        self.assertTrue(all(evt.participant_db_id is not None for evt in order_repo.orders))


if __name__ == "__main__":
    unittest.main()

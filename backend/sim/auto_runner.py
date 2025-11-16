"""Background auto-tick runner for simulation sessions."""
from __future__ import annotations

import asyncio
import contextlib
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, Sequence, Optional, TYPE_CHECKING
import uuid

from .repositories import SimulationRepository
from .services import SimulationService
from .types import SimulationSession

if TYPE_CHECKING:  # pragma: no cover
    from .cache import SimulationCache
    from .agents import AgentRegistry


@dataclass(slots=True)
class _SessionState:
    session_id: int
    next_tick: int


class SimulationAutoRunner:
    """Drives simulation ticks for configured sessions without external requests."""

    def __init__(
        self,
        *,
        service: SimulationService,
        session_repo: SimulationRepository,
        session_codes: Sequence[str],
        interval_ms: int = 500,
        mode: str = "autoplay",
        cache: Optional["SimulationCache"] = None,
        verbose: bool = False,
        bootstrap_price: float = 100.0,
        bootstrap_spread: float = 0.4,
        bootstrap_volume: float = 20.0,
        session_profiles: Optional[Dict[str, Dict[str, Any]]] = None,
        logger: Optional[logging.Logger] = None,
        agent_registry: Optional["AgentRegistry"] = None,
    ) -> None:
        self._service = service
        self._session_repo = session_repo
        self._session_codes = [code.strip() for code in session_codes if code.strip()]
        self._interval = max(interval_ms, 50) / 1000.0
        self._mode = mode
        self._cache = cache
        self._verbose = verbose
        self._bootstrap_price = max(bootstrap_price, 0.01)
        self._bootstrap_spread = max(bootstrap_spread, 0.01)
        self._bootstrap_volume = max(bootstrap_volume, 1.0)
        self._session_profiles = session_profiles or {}
        default_logger = logging.getLogger("uvicorn.error")
        self._logger = logger or default_logger
        if verbose:
            self._logger.setLevel(logging.INFO)
        self._session_state: Dict[str, _SessionState] = {}
        self._task: Optional[asyncio.Task[None]] = None
        self._agent_registry = agent_registry

    async def start(self) -> None:
        """Ensure sessions exist and start the background loop."""
        if not self._session_codes:
            self._logger.info("SimulationAutoRunner: no sessions configured, skipping start.")
            return
        await self._ensure_sessions()
        await self._bootstrap_sessions()
        if not self._session_state:
            self._logger.warning("SimulationAutoRunner: failed to initialize any sessions.")
            return
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._run_loop())
        self._logger.info(
            "SimulationAutoRunner started for sessions: %s",
            ", ".join(self._session_state.keys()),
        )

    async def stop(self) -> None:
        """Stop the background loop gracefully."""
        task = self._task
        if task is None:
            return
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        self._task = None
        self._logger.info("SimulationAutoRunner stopped.")

    async def _ensure_sessions(self) -> None:
        for code in self._session_codes:
            await self._ensure_session(code)

    async def _bootstrap_sessions(self) -> None:
        for code, state in self._session_state.items():
            if state.next_tick <= 0:
                await self._run_bootstrap_tick(code, state)

    async def _register_default_agents(self, session_id: int, session_code: str) -> None:
        """Register default AI agents for a newly created session."""
        try:
            from .agents import (
                PropMomentumAgent,
                InstitutionalRebalanceAgent,
                RetailSentimentAgent,
                MarketMakerAgent,
            )

            self._logger.info(
                "Registering AI agents for session: %s (ID: %d)",
                session_code,
                session_id,
            )

            # Prop Traders expanded pool - multiple archetypes
            prop_profiles = [
                {
                    "prefix": "prop-aggressive",
                    "count": 12,
                    "profit_target": 0.05,
                    "stop_loss": 0.02,
                    "risk_tolerance": 0.9,
                    "momentum_sensitivity": 0.95,
                    "weight": 1.2,
                    "cash_range": (80_000_000.0, 120_000_000.0),
                },
                {
                    "prefix": "prop-balanced",
                    "count": 10,
                    "profit_target": 0.03,
                    "stop_loss": 0.015,
                    "risk_tolerance": 0.7,
                    "momentum_sensitivity": 0.85,
                    "weight": 1.0,
                    "cash_range": (45_000_000.0, 70_000_000.0),
                },
                {
                    "prefix": "prop-conservative",
                    "count": 8,
                    "profit_target": 0.02,
                    "stop_loss": 0.01,
                    "risk_tolerance": 0.5,
                    "momentum_sensitivity": 0.7,
                    "weight": 0.85,
                    "cash_range": (20_000_000.0, 45_000_000.0),
                },
            ]

            for profile in prop_profiles:
                for idx in range(profile["count"]):
                    code = f"{profile['prefix']}-{idx + 1}"
                    cash = random.uniform(*profile["cash_range"])
                    await self._agent_registry.register(
                        session_id=session_id,
                        agent=PropMomentumAgent(
                            code=code,
                            base_quantity=120.0,
                            profit_target=profile["profit_target"],
                            stop_loss=profile["stop_loss"],
                            risk_tolerance=profile["risk_tolerance"],
                            momentum_sensitivity=profile["momentum_sensitivity"],
                            weight=profile["weight"],
                            initial_cash=cash,
                        ),
                        weight=profile["weight"],
                        pool_code="prop",
                    )

            # Institutional Investors (3 agents) - 机构 10亿
            inst_configs = [
                ("inst-large-1", 200.0, 0.02, 100, 0.02, 150.0, True, 0.4, 0.2, 1.5, 1000000000.0),  # 10亿
                ("inst-medium-1", 100.0, 0.025, 50, 0.03, 100.0, True, 0.6, 0.3, 1.0, 1000000000.0), # 10亿
                ("inst-medium-2", 100.0, 0.025, 50, 0.03, 100.0, True, 0.6, 0.3, 1.0, 1000000000.0), # 10亿
            ]

            for code, base_qty, dd_target, mr_window, rebal_thresh, max_order, split, risk_tol, herd, weight, cash in inst_configs:
                await self._agent_registry.register(
                    session_id=session_id,
                    agent=InstitutionalRebalanceAgent(
                        code=code,
                        base_quantity=base_qty,
                        drawdown_target=dd_target,
                        mean_reversion_window=mr_window,
                        rebalance_threshold=rebal_thresh,
                        max_order_size=max_order,
                        split_orders=split,
                        risk_tolerance=risk_tol,
                        herd_behavior_strength=herd,
                        weight=weight,  # Pass weight to agent
                        initial_cash=cash,
                    ),
                    weight=weight,
                    pool_code="institutional",
                )

            # Retail Traders expanded (200 agents with varying behavior) - 散户 10-50万
            # 强跟风散户：100个，资金10-20万
            for i in range(100):
                cash = random.uniform(100000.0, 200000.0)  # 10-20万
                await self._agent_registry.register(
                    session_id=session_id,
                    agent=RetailSentimentAgent(
                        code=f"retail-follower-{i+1}",
                        base_quantity=30.0,
                        herd_behavior_strength=0.9,
                        momentum_sensitivity=0.8,
                        risk_tolerance=0.7,
                        weight=0.6,  # Pass weight to agent
                        initial_cash=cash,
                    ),
                    weight=0.6,
                    pool_code="retail",
                )

            # 适度跟风散户：60个，资金20-35万
            for i in range(60):
                cash = random.uniform(200000.0, 350000.0)  # 20-35万
                await self._agent_registry.register(
                    session_id=session_id,
                    agent=RetailSentimentAgent(
                        code=f"retail-moderate-{i+1}",
                        base_quantity=40.0,
                        herd_behavior_strength=0.5,
                        momentum_sensitivity=0.6,
                        risk_tolerance=0.5,
                        weight=0.8,  # Pass weight to agent
                        initial_cash=cash,
                    ),
                    weight=0.8,
                    pool_code="retail",
                )

            # 独立散户：40个，资金35-50万
            for i in range(40):
                cash = random.uniform(350000.0, 500000.0)  # 35-50万
                await self._agent_registry.register(
                    session_id=session_id,
                    agent=RetailSentimentAgent(
                        code=f"retail-independent-{i+1}",
                        base_quantity=50.0,
                        herd_behavior_strength=0.2,
                        momentum_sensitivity=0.4,
                        risk_tolerance=0.6,
                        weight=1.0,  # Pass weight to agent
                        initial_cash=cash,
                    ),
                    weight=1.0,
                    pool_code="retail",
                )

            # 反向散户：30个，挂反向限价
            for i in range(30):
                cash = random.uniform(300000.0, 450000.0)
                await self._agent_registry.register(
                    session_id=session_id,
                    agent=RetailSentimentAgent(
                        code=f"retail-contrarian-{i+1}",
                        base_quantity=45.0,
                        herd_behavior_strength=0.1,
                        momentum_sensitivity=0.3,
                        risk_tolerance=0.5,
                        weight=0.9,
                        initial_cash=cash,
                        contrarian=True,
                    ),
                    weight=0.9,
                    pool_code="retail",
                )

            # Market Makers (2 agents) - provides liquidity with limit orders - 做市商 1亿
            # Primary market maker with tighter spread
            await self._agent_registry.register(
                session_id=session_id,
                agent=MarketMakerAgent(
                    code="mm-primary",
                    spread_bps=15.0,  # 0.15% spread (tighter)
                    base_quantity=35.0,
                    levels=50,  # 50 levels on each side
                    level_spacing_bps=8.0,  # 0.08% between levels
                    decay=0.85,  # Quantity decays per level
                    refresh_interval=5,  # Refresh every 5 ticks
                    weight=1.5,  # Pass weight to agent
                    initial_cash=100000000.0,  # 1亿资金
                ),
                weight=1.5,
                pool_code="market_maker",
            )

            # Secondary market maker with wider spread for deeper liquidity
            await self._agent_registry.register(
                session_id=session_id,
                agent=MarketMakerAgent(
                    code="mm-secondary",
                    spread_bps=25.0,  # 0.25% spread (wider)
                    base_quantity=40.0,
                    levels=50,  # 50 levels on each side
                    level_spacing_bps=12.0,  # 0.12% between levels
                    decay=0.88,  # Slower decay for deeper support
                    refresh_interval=7,  # Refresh every 7 ticks
                    weight=1.3,
                    initial_cash=100000000.0,  # 1亿资金
                ),
                weight=1.3,
                pool_code="market_maker",
            )

            total_prop_agents = sum(profile["count"] for profile in prop_profiles)
            total_retail = 100 + 60 + 40 + 30
            total_agents = total_prop_agents + 3 + total_retail + 2
            self._logger.info(
                "Successfully registered %d AI agents for session %s (%d prop, 3 institutional, %d retail, 2 market makers)",
                total_agents,
                session_code,
                total_prop_agents,
                total_retail,
            )

            # Immediately persist agents to database for API visibility
            await self._persist_agents_to_db(session_id)

        except Exception as exc:
            self._logger.error(
                "Failed to register AI agents for session %s: %s",
                session_code,
                exc,
            )

    async def _persist_agents_to_db(self, session_id: int) -> None:
        """Persist registered agents to database immediately after registration."""
        try:
            # Get all registered agents for this session
            agents = self._agent_registry._agents.get(session_id, [])
            if not agents:
                return

            # Build payloads for each agent
            payloads = []
            for entry in agents:
                agent = entry.strategy
                payload = {
                    "participant_code": agent.code,
                    "participant_type": "agent",
                    "behavior_category": getattr(agent, "behavior_category", None) or entry.pool_code,
                    "profit_target": getattr(agent, "profit_target", None),
                    "stop_loss": getattr(agent, "stop_loss", None),
                    "herd_behavior_strength": getattr(agent, "herd_behavior_strength", None),
                    "momentum_sensitivity": getattr(agent, "momentum_sensitivity", None),
                    "risk_tolerance": getattr(agent, "risk_tolerance", None),
                }
                payloads.append(payload)

            # Persist to database
            await self._session_repo.ensure_participants_bulk(session_id, payloads)
            self._logger.info(
                "Persisted %d agents to database for session %d",
                len(payloads),
                session_id,
            )

        except Exception as exc:
            self._logger.error(
                "Failed to persist agents to database for session %d: %s",
                session_id,
                exc,
            )

    async def _ensure_session(self, session_code: str) -> None:
        session = await self._session_repo.fetch_session_by_code(session_code)
        session_created = False
        if session is None:
            session = SimulationSession(
                id=None,
                session_code=session_code,
                status="running",
                mode=self._mode,
                tick_interval_ms=int(self._interval * 1000),
                total_ticks=0,
                config_version="auto",
            )
            session = await self._service.create_session(session)
            session_created = True
            if session.id is None:  # pragma: no cover - defensive
                self._logger.error("SimulationAutoRunner: failed to create session %s", session_code)
                return
            await self._service.update_tick(session.id, 0)
            if self._cache is not None:
                await self._cache.set_status(session_code, "running")
                await self._cache.set_tick(session_code, 0)
        if session.id is None:
            self._logger.error("SimulationAutoRunner: session %s has no id, skipping", session_code)
            return
        next_tick = session.current_tick or 0
        self._session_state[session_code] = _SessionState(
            session_id=session.id,
            next_tick=next_tick,
        )
        profile = self._session_profiles.get(session_code, {}).copy()
        # Ensure initial_price is set from bootstrap_price if not explicitly provided
        if "initial_price" not in profile:
            profile["initial_price"] = self._bootstrap_price
        self._service.set_session_profile(session.id, profile)

        # Register AI agents for sessions (both new and existing)
        if self._agent_registry is not None:
            # Check if agents are already registered for this session
            has_agents = await self._agent_registry.has_agents(session.id)
            if not has_agents:
                self._logger.info(
                    "No agents found for session %s (ID: %d), registering default agents",
                    session_code,
                    session.id,
                )
                await self._register_default_agents(session.id, session_code)
            else:
                self._logger.info(
                    "Agents already registered for session %s (ID: %d), skipping registration",
                    session_code,
                    session.id,
                )

    async def _run_bootstrap_tick(self, session_code: str, state: _SessionState) -> None:
        tick = state.next_tick + 1
        base_price = self._bootstrap_price
        spread = self._bootstrap_spread
        volume = self._bootstrap_volume
        market_qty = max(volume * 0.2, 1.0)
        limit_bid_price = max(base_price - spread / 2, 0.01)
        limit_ask_price = base_price + spread / 2
        participant = "auto-bootstrap"

        def oid(suffix: str) -> str:
            return f"{participant}-{tick}-{suffix}-{uuid.uuid4().hex[:6]}"

        orders = [
            {
                "order_id": oid("bid"),
                "participant_id": f"{participant}-maker",
                "participant_code": f"{participant}-maker",
                "participant_type": "agent",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": volume,
                "price": round(limit_bid_price, 4),
            },
            {
                "order_id": oid("ask"),
                "participant_id": f"{participant}-maker",
                "participant_code": f"{participant}-maker",
                "participant_type": "agent",
                "side": "SELL",
                "type": "LIMIT",
                "quantity": volume,
                "price": round(limit_ask_price, 4),
            },
            {
                "order_id": oid("mkt-buy"),
                "participant_id": f"{participant}-seed",
                "participant_code": f"{participant}-seed",
                "participant_type": "agent",
                "side": "BUY",
                "type": "MARKET",
                "quantity": market_qty,
            },
            {
                "order_id": oid("mkt-sell"),
                "participant_id": f"{participant}-seed",
                "participant_code": f"{participant}-seed",
                "participant_type": "agent",
                "side": "SELL",
                "type": "MARKET",
                "quantity": market_qty,
            },
        ]

        try:
            await self._service.process_tick(
                session_id=state.session_id,
                session_code=session_code,
                tick=tick,
                orders=orders,
                timestamp=datetime.now(timezone.utc),
            )
            state.next_tick = tick
            self._logger.info(
                "AutoTick bootstrap session=%s tick=%s price≈%s",
                session_code,
                tick,
                base_price,
            )
        except Exception as exc:
            self._logger.warning(
                "SimulationAutoRunner bootstrap failed session=%s: %s",
                session_code,
                exc,
            )

    async def _run_loop(self) -> None:
        try:
            while True:
                loop_started = perf_counter()
                for code in self._session_codes:
                    state = self._session_state.get(code)
                    if state is None:
                        await self._ensure_session(code)
                        state = self._session_state.get(code)
                        if state is None:
                            continue
                    tick = state.next_tick + 1
                    try:
                        result = await self._service.process_tick(
                            session_id=state.session_id,
                            session_code=code,
                            tick=tick,
                            orders=[],
                            timestamp=datetime.now(timezone.utc),
                        )
                        state.next_tick = tick
                        if self._verbose:
                            snapshot = result.get("snapshot") if isinstance(result, dict) else None
                            last_price = snapshot.get("last_price") if snapshot else None
                            trades = result.get("trades") if isinstance(result, dict) else None
                            orders = result.get("orders") if isinstance(result, dict) else None
                            self._logger.info(
                                "AutoTick session=%s tick=%s price=%s orders=%d trades=%d",
                                code,
                                tick,
                                (
                                    f"{last_price:.2f}"
                                    if isinstance(last_price, (int, float))
                                    else last_price
                                ),
                                len(orders or []),
                                len(trades or []),
                            )
                    except Exception as exc:  # pragma: no cover - keep runner alive
                        self._logger.warning(
                            "SimulationAutoRunner tick failure session=%s tick=%s: %s",
                            code,
                            tick,
                            exc,
                        )
                elapsed = perf_counter() - loop_started
                await asyncio.sleep(max(self._interval - elapsed, 0.01))
        except asyncio.CancelledError:
            raise
        finally:
            self._logger.debug("SimulationAutoRunner loop exiting.")


__all__ = ["SimulationAutoRunner"]

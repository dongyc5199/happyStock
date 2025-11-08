"""AI coach insight generation utilities."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Sequence

from .types import CoachInsight, MarketSnapshot, TradeEventRecord


class CoachInsightBuilder:
    """Produce AI 教练日志，基于当前 tick 的成交与行情信号。"""

    def __init__(
        self,
        *,
        large_trade_ratio: float = 0.2,
        min_volume: float = 1.0,
    ) -> None:
        self._large_trade_ratio = large_trade_ratio
        self._min_volume = min_volume

    def build(
        self,
        *,
        session_id: int,
        session_code: str,
        tick: int,
        snapshot: MarketSnapshot,
        trades: Sequence[TradeEventRecord],
        score_deltas: Dict[str, float],
        created_at: datetime | None = None,
    ) -> List[CoachInsight]:
        if not trades:
            return []

        created_at = created_at or datetime.now(timezone.utc)
        stats = self._aggregate_participant_stats(trades)
        insights: List[CoachInsight] = []

        threshold = max(
            self._min_volume,
            (snapshot.total_volume or 0.0) * self._large_trade_ratio,
        )

        for participant_id, data in stats.items():
            total_volume = data["buy_volume"] + data["sell_volume"]
            if total_volume < self._min_volume:
                continue

            net_volume = data["buy_volume"] - data["sell_volume"]
            avg_price = (
                data["notional"] / total_volume if total_volume > 0 else snapshot.last_price
            )
            participant_type = self._infer_participant_type(participant_id)
            score_delta = score_deltas.get(participant_id, 0.0)
            sentiment = snapshot.emotion if snapshot.emotion is not None else 0.0
            imbalance = snapshot.imbalance if snapshot.imbalance is not None else 0.0

            direction = self._direction_label(net_volume)
            participant_label = "玩家" if participant_type == "player" else "智能体"

            headline = self._compose_headline(direction, net_volume)
            summary = (
                f"{participant_label}「{participant_id}」在 tick {tick} {direction}"
                f"{abs(net_volume):.2f} 手，成交均价 {avg_price:.2f}。"
                f" 盘口不平衡度 {imbalance:+.2f}，情绪指数 {sentiment:+.2f}。"
            )

            recommendations = self._compose_recommendations(
                net_volume=net_volume,
                imbalance=imbalance,
                sentiment=sentiment,
                score_delta=score_delta,
            )

            severity = "info"
            category = "positioning"
            if abs(net_volume) >= threshold or score_delta < 0:
                severity = "warning"
                category = "risk"

            metrics = {
                "buy_volume": round(data["buy_volume"], 4),
                "sell_volume": round(data["sell_volume"], 4),
                "net_volume": round(net_volume, 4),
                "avg_trade_price": round(avg_price or 0.0, 4),
                "score_delta": round(score_delta, 4),
                "trade_count": data["trade_count"],
                "sentiment": round(sentiment, 4),
                "order_book_imbalance": round(imbalance, 4),
                "last_price": snapshot.last_price,
            }

            insights.append(
                CoachInsight(
                    session_id=session_id,
                    session_code=session_code,
                    tick=tick,
                    participant_id=participant_id,
                    participant_db_id=data["participant_db_id"],
                    participant_type=participant_type,
                    category=category,
                    severity=severity,
                    headline=headline,
                    summary=summary,
                    metrics=metrics,
                    recommendations=recommendations,
                    created_at=created_at,
                )
            )

        return insights

    def _aggregate_participant_stats(
        self, trades: Sequence[TradeEventRecord]
    ) -> Dict[str, Dict[str, float]]:
        stats: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "buy_volume": 0.0,
                "sell_volume": 0.0,
                "notional": 0.0,
                "trade_count": 0,
                "participant_db_id": None,
            }
        )

        for trade in trades:
            if trade.buyer_participant_id:
                buyer = stats[trade.buyer_participant_id]
                buyer["buy_volume"] += trade.quantity
                buyer["notional"] += trade.quantity * trade.price
                buyer["trade_count"] += 1
                if trade.buyer_participant_db_id is not None:
                    buyer["participant_db_id"] = trade.buyer_participant_db_id

            if trade.seller_participant_id:
                seller = stats[trade.seller_participant_id]
                seller["sell_volume"] += trade.quantity
                seller["notional"] += trade.quantity * trade.price
                seller["trade_count"] += 1
                if trade.seller_participant_db_id is not None:
                    seller["participant_db_id"] = trade.seller_participant_db_id

        return stats

    @staticmethod
    def _infer_participant_type(participant_id: str) -> str:
        lowered = participant_id.lower()
        if lowered.startswith(("agent", "prop", "inst", "mm")):
            return "agent"
        return "player"

    @staticmethod
    def _direction_label(net_volume: float) -> str:
        if net_volume > 0:
            return "净买入"
        if net_volume < 0:
            return "净卖出"
        return "保持观望"

    @staticmethod
    def _compose_headline(direction: str, net_volume: float) -> str:
        if direction == "保持观望":
            return "保持观望，等待更优价格"
        return f"{direction} {abs(net_volume):.2f} 手"

    @staticmethod
    def _compose_recommendations(
        *,
        net_volume: float,
        imbalance: float,
        sentiment: float,
        score_delta: float,
    ) -> List[str]:
        recs: List[str] = []

        if abs(imbalance) >= 0.4:
            recs.append("盘口极度不均衡，建议缩小委托尺寸或拆分执行。")
        if sentiment >= 0.6 and net_volume > 0:
            recs.append("市场情绪偏热，留意追高后的回落风险。")
        if sentiment <= -0.4 and net_volume < 0:
            recs.append("情绪低迷，适度分批回补可降低踏空概率。")
        if score_delta < 0:
            recs.append("收益走弱，建议复盘仓位结构与止损线。")

        if not recs:
            recs.append("保持当前节奏，重点观察流动性与成交密度变化。")

        return recs


__all__ = ["CoachInsightBuilder"]

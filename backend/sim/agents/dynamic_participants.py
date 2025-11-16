"""
动态参与者管理系统

根据市场走势动态增加新的 AI 参与者（散户、游资、机构）
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List
from dataclasses import dataclass

if TYPE_CHECKING:
    from .registry import AgentRegistry
    from .base import AgentStrategy

logger = logging.getLogger(__name__)


@dataclass
class MarketCondition:
    """市场状况"""
    price_change_pct: float  # 价格变化百分比
    volume_surge: float  # 成交量激增倍数
    sentiment: float  # 市场情绪 (-1 to 1)
    volatility: float  # 波动率
    tick: int  # 当前 tick


@dataclass
class ParticipantConfig:
    """参与者配置"""
    agent_type: str  # "retail", "prop", "institutional"
    base_probability: float  # 基础入场概率
    price_sensitivity: float  # 价格敏感度
    volume_sensitivity: float  # 成交量敏感度
    sentiment_sensitivity: float  # 情绪敏感度
    max_count: int  # 最大数量


class DynamicParticipantManager:
    """
    动态参与者管理器

    职责：
    1. 监控市场状况
    2. 根据条件触发新参与者入场
    3. 维护参与者数量比例（散户占比最大）
    """

    def __init__(
        self,
        *,
        retail_max: int = 50,  # 散户最大数量
        prop_max: int = 10,  # 游资最大数量
        institutional_max: int = 5,  # 机构最大数量
        evaluation_interval: int = 10,  # 每 N tick 评估一次
    ):
        self.retail_max = retail_max
        self.prop_max = prop_max
        self.institutional_max = institutional_max
        self.evaluation_interval = evaluation_interval

        # 参与者配置
        self.configs = {
            "retail": ParticipantConfig(
                agent_type="retail",
                base_probability=0.3,  # 散户最容易入场
                price_sensitivity=0.8,  # 对价格上涨敏感
                volume_sensitivity=0.5,
                sentiment_sensitivity=0.9,  # 对情绪敏感
                max_count=retail_max,
            ),
            "prop": ParticipantConfig(
                agent_type="prop",
                base_probability=0.15,  # 游资较谨慎
                price_sensitivity=0.6,
                volume_sensitivity=0.8,  # 对成交量敏感
                sentiment_sensitivity=0.4,
                max_count=prop_max,
            ),
            "institutional": ParticipantConfig(
                agent_type="institutional",
                base_probability=0.05,  # 机构最谨慎
                price_sensitivity=0.3,
                volume_sensitivity=0.7,
                sentiment_sensitivity=0.2,  # 机构理性
                max_count=institutional_max,
            ),
        }

        # 追踪每个会话的参与者计数
        self._participant_counts: Dict[int, Dict[str, int]] = {}
        # session_id -> {"retail": count, "prop": count, "institutional": count}

        # 追踪市场历史用于计算趋势
        self._price_history: Dict[int, List[float]] = {}  # session_id -> prices
        self._volume_history: Dict[int, List[float]] = {}  # session_id -> volumes

    def _ensure_session(self, session_id: int) -> None:
        """初始化会话数据"""
        if session_id not in self._participant_counts:
            self._participant_counts[session_id] = {
                "retail": 0,
                "prop": 0,
                "institutional": 0,
            }
            self._price_history[session_id] = []
            self._volume_history[session_id] = []

    def update_market_data(
        self,
        session_id: int,
        price: float,
        volume: float,
    ) -> None:
        """更新市场数据历史"""
        self._ensure_session(session_id)

        # 保留最近 100 个数据点
        if len(self._price_history[session_id]) >= 100:
            self._price_history[session_id].pop(0)
        if len(self._volume_history[session_id]) >= 100:
            self._volume_history[session_id].pop(0)

        self._price_history[session_id].append(price)
        self._volume_history[session_id].append(volume)

    def _calculate_market_condition(
        self,
        session_id: int,
        current_sentiment: float,
        current_volatility: float,
        tick: int,
    ) -> MarketCondition:
        """计算当前市场状况"""
        self._ensure_session(session_id)

        prices = self._price_history[session_id]
        volumes = self._volume_history[session_id]

        # 价格变化（最近 10 个 tick）
        price_change_pct = 0.0
        if len(prices) >= 10:
            old_price = prices[-10]
            new_price = prices[-1]
            if old_price > 0:
                price_change_pct = (new_price - old_price) / old_price

        # 成交量激增（对比平均值）
        volume_surge = 1.0
        if len(volumes) >= 20:
            avg_volume = sum(volumes[-20:-5]) / 15  # 前 15 个 tick 平均
            recent_volume = sum(volumes[-5:]) / 5  # 最近 5 个 tick 平均
            if avg_volume > 0:
                volume_surge = recent_volume / avg_volume

        return MarketCondition(
            price_change_pct=price_change_pct,
            volume_surge=volume_surge,
            sentiment=current_sentiment,
            volatility=current_volatility,
            tick=tick,
        )

    def _calculate_entry_probability(
        self,
        config: ParticipantConfig,
        condition: MarketCondition,
    ) -> float:
        """
        计算新参与者入场概率

        基础概率 + 各种因素加成
        """
        probability = config.base_probability

        # 价格上涨加成（上涨越多，越吸引人）
        if condition.price_change_pct > 0:
            price_boost = condition.price_change_pct * config.price_sensitivity * 2.0
            probability += price_boost

        # 成交量激增加成
        if condition.volume_surge > 1.2:  # 成交量超过平均 20%
            volume_boost = (condition.volume_surge - 1.0) * config.volume_sensitivity * 0.3
            probability += volume_boost

        # 情绪加成（正面情绪吸引入场）
        if condition.sentiment > 0:
            sentiment_boost = condition.sentiment * config.sentiment_sensitivity * 0.5
            probability += sentiment_boost

        # 波动率加成（高波动吸引游资和散户，但不吸引机构）
        if config.agent_type in ["retail", "prop"]:
            if condition.volatility > 0.03:  # 波动率 > 3%
                volatility_boost = (condition.volatility - 0.03) * 3.0
                probability += volatility_boost

        # 限制在 [0, 1] 范围
        return max(0.0, min(1.0, probability))

    def should_add_participant(
        self,
        session_id: int,
        agent_type: str,
        condition: MarketCondition,
    ) -> bool:
        """判断是否应该添加新参与者"""
        self._ensure_session(session_id)

        config = self.configs.get(agent_type)
        if config is None:
            return False

        # 检查是否达到最大数量
        current_count = self._participant_counts[session_id][agent_type]
        if current_count >= config.max_count:
            return False

        # 检查是否到了评估时间
        if condition.tick % self.evaluation_interval != 0:
            return False

        # 计算入场概率
        probability = self._calculate_entry_probability(config, condition)

        # 使用随机数判断
        import random
        return random.random() < probability

    def increment_count(self, session_id: int, agent_type: str) -> None:
        """增加参与者计数"""
        self._ensure_session(session_id)
        if agent_type in self._participant_counts[session_id]:
            self._participant_counts[session_id][agent_type] += 1

    def get_counts(self, session_id: int) -> Dict[str, int]:
        """获取当前参与者数量"""
        self._ensure_session(session_id)
        return self._participant_counts[session_id].copy()

    def get_total_count(self, session_id: int) -> int:
        """获取总参与者数量"""
        counts = self.get_counts(session_id)
        return sum(counts.values())

    def get_participant_distribution(self, session_id: int) -> Dict[str, float]:
        """获取参与者分布百分比"""
        counts = self.get_counts(session_id)
        total = sum(counts.values())
        if total == 0:
            return {"retail": 0.0, "prop": 0.0, "institutional": 0.0}

        return {
            agent_type: count / total
            for agent_type, count in counts.items()
        }

    def create_new_participant(
        self,
        session_id: int,
        agent_type: str,
        sequence_number: int,
    ) -> "AgentStrategy":
        """
        创建新的参与者代理

        根据类型创建不同配置的代理
        """
        from .retail import RetailSentimentAgent
        from .prop import PropMomentumAgent
        from .institutional import InstitutionalRebalanceAgent
        import random

        if agent_type == "retail":
            # 散户：随机羊群强度
            herd_strength = random.uniform(0.4, 0.95)
            initial_cash = random.uniform(30000, 80000)
            return RetailSentimentAgent(
                code=f"retail-dynamic-{sequence_number}",
                base_quantity=random.uniform(20.0, 50.0),
                herd_behavior_strength=herd_strength,
                momentum_sensitivity=random.uniform(0.5, 0.9),
                risk_tolerance=random.uniform(0.5, 0.8),
                initial_cash=initial_cash,
            )

        elif agent_type == "prop":
            # 游资：随机风险偏好
            risk_level = random.choice(["aggressive", "balanced", "conservative"])
            if risk_level == "aggressive":
                return PropMomentumAgent(
                    code=f"prop-dynamic-{sequence_number}",
                    base_quantity=random.uniform(80.0, 150.0),
                    profit_target=random.uniform(0.04, 0.06),
                    stop_loss=random.uniform(0.015, 0.025),
                    risk_tolerance=random.uniform(0.8, 0.95),
                    initial_cash=random.uniform(120000, 200000),
                )
            elif risk_level == "balanced":
                return PropMomentumAgent(
                    code=f"prop-dynamic-{sequence_number}",
                    base_quantity=random.uniform(60.0, 120.0),
                    profit_target=random.uniform(0.025, 0.04),
                    stop_loss=random.uniform(0.01, 0.02),
                    risk_tolerance=random.uniform(0.6, 0.8),
                    initial_cash=random.uniform(100000, 150000),
                )
            else:  # conservative
                return PropMomentumAgent(
                    code=f"prop-dynamic-{sequence_number}",
                    base_quantity=random.uniform(40.0, 80.0),
                    profit_target=random.uniform(0.015, 0.03),
                    stop_loss=random.uniform(0.008, 0.015),
                    risk_tolerance=random.uniform(0.4, 0.6),
                    initial_cash=random.uniform(80000, 120000),
                )

        elif agent_type == "institutional":
            # 机构：较为统一的策略
            return InstitutionalRebalanceAgent(
                code=f"inst-dynamic-{sequence_number}",
                base_quantity=random.uniform(150.0, 300.0),
                mean_reversion_window=random.randint(50, 150),
                rebalance_threshold=random.uniform(0.015, 0.03),
                split_orders=True,
                initial_cash=random.uniform(300000, 600000),
            )

        else:
            raise ValueError(f"Unknown agent type: {agent_type}")


__all__ = ["DynamicParticipantManager", "MarketCondition", "ParticipantConfig"]

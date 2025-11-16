"""
Behavior parameter definitions for AI agents (T057-T059).

Feature: 001-ai-user-order-matching, Phase 5, US2
"""
from dataclasses import dataclass, field
from typing import Literal


AgentCategory = Literal["institutional", "prop", "retail", "market_maker"]


@dataclass(slots=True)
class InstitutionalBehavior:
    """
    T057: Institutional investor behavior parameters.

    Characteristics:
    - Goal: Long-term value investing, portfolio rebalancing
    - Risk: Low, prefers diversified holdings
    - Trade size: Large block trades
    - Frequency: Low, periodic rebalancing

    UPDATED: Increased sensitivity based on simulation analysis
    """
    behavior_category: Literal["institutional"] = "institutional"

    # Profit/loss management
    profit_target: float = 0.15  # 15% annual target
    stop_loss: float = -0.08     # -8% max drawdown before rebalancing

    # Trading behavior
    herd_behavior_strength: float = 0.2    # Low herd mentality (0-1)
    momentum_sensitivity: float = 0.3      # Low momentum chasing (0-1)
    risk_tolerance: float = 0.4            # Moderate risk tolerance (0-1)

    # Strategy-specific (InstitutionalRebalanceAgent)
    drawdown_target: float = 0.02          # ADJUSTED: 0.04 -> 0.02 (trigger at 2% drawdown, more proactive)
    base_quantity: float = 50.0            # Base order size
    block_interval_ticks: tuple[int, int] = (1200, 2400)  # 20-40 min between blocks
    block_multiplier: float = 6.0          # Block trade size multiplier

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "behavior_category": self.behavior_category,
            "profit_target": self.profit_target,
            "stop_loss": self.stop_loss,
            "herd_behavior_strength": self.herd_behavior_strength,
            "momentum_sensitivity": self.momentum_sensitivity,
            "risk_tolerance": self.risk_tolerance,
        }


@dataclass(slots=True)
class PropTraderBehavior:
    """
    T058: Proprietary trader (游资) behavior parameters.

    Characteristics:
    - Goal: Short-term momentum trading, profit from volatility
    - Risk: High, aggressive position sizing
    - Trade size: Medium to large, frequent bursts
    - Frequency: High during volatile periods
    """
    behavior_category: Literal["prop"] = "prop"

    # Profit/loss management
    profit_target: float = 0.50   # 50% aggressive profit target
    stop_loss: float = -0.15      # -15% stop loss

    # Trading behavior
    herd_behavior_strength: float = 0.4    # Moderate, follows momentum (0-1)
    momentum_sensitivity: float = 0.85     # Very high momentum sensitivity (0-1)
    risk_tolerance: float = 0.75           # High risk tolerance (0-1)

    # Strategy-specific (PropMomentumAgent)
    volatility_trigger: float = 0.02       # Trade when volatility > 2%
    base_quantity: float = 120.0           # Larger base size than retail
    trend_sensitivity: float = 0.6         # How much to weight price trend
    noise: float = 0.15                    # Random noise in decisions
    burst_interval_ticks: tuple[int, int] = (60, 160)  # 1-2.5 min between bursts
    burst_multiplier: float = 3.5          # Burst trade size multiplier

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "behavior_category": self.behavior_category,
            "profit_target": self.profit_target,
            "stop_loss": self.stop_loss,
            "herd_behavior_strength": self.herd_behavior_strength,
            "momentum_sensitivity": self.momentum_sensitivity,
            "risk_tolerance": self.risk_tolerance,
        }


@dataclass(slots=True)
class RetailBehavior:
    """
    T059: Retail investor (散户) behavior parameters.

    Characteristics:
    - Goal: Follow trends and sentiment, often FOMO-driven
    - Risk: Variable, often high due to inexperience
    - Trade size: Small
    - Frequency: Reactive to market moves and news

    UPDATED: Increased activity based on simulation analysis
    """
    behavior_category: Literal["retail"] = "retail"

    # Profit/loss management
    profit_target: float = 0.30   # 30% hopeful target
    stop_loss: float = -0.20      # -20% poor risk management

    # Trading behavior
    herd_behavior_strength: float = 0.75   # High herd mentality (0-1)
    momentum_sensitivity: float = 0.60     # Moderate to high (0-1)
    risk_tolerance: float = 0.55           # Moderate (often overestimate) (0-1)

    # Strategy-specific (RetailSentimentAgent)
    threshold: float = 0.03                # ADJUSTED: 0.05 -> 0.03 (more sensitive, easier to trigger)
    base_quantity: float = 5.0             # Small order size
    follow_chance: float = 0.45            # ADJUSTED: 0.35 -> 0.45 (more FOMO-driven)

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "behavior_category": self.behavior_category,
            "profit_target": self.profit_target,
            "stop_loss": self.stop_loss,
            "herd_behavior_strength": self.herd_behavior_strength,
            "momentum_sensitivity": self.momentum_sensitivity,
            "risk_tolerance": self.risk_tolerance,
        }


@dataclass(slots=True)
class MarketMakerBehavior:
    """
    Market maker behavior parameters (for completeness).

    Characteristics:
    - Goal: Provide liquidity, profit from spread
    - Risk: Very low, hedged positions
    - Trade size: Varies based on inventory
    - Frequency: Continuous quote updates
    """
    behavior_category: Literal["market_maker"] = "market_maker"

    # Profit/loss management
    profit_target: float = 0.10   # 10% consistent returns
    stop_loss: float = -0.05      # -5% tight risk control

    # Trading behavior
    herd_behavior_strength: float = 0.1    # Very low, contrarian (0-1)
    momentum_sensitivity: float = 0.2      # Low, mean-reverting (0-1)
    risk_tolerance: float = 0.3            # Low risk tolerance (0-1)

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "behavior_category": self.behavior_category,
            "profit_target": self.profit_target,
            "stop_loss": self.stop_loss,
            "herd_behavior_strength": self.herd_behavior_strength,
            "momentum_sensitivity": self.momentum_sensitivity,
            "risk_tolerance": self.risk_tolerance,
        }


# Default parameter sets for each agent type
DEFAULT_BEHAVIORS: dict[AgentCategory, dict] = {
    "institutional": InstitutionalBehavior().to_dict(),
    "prop": PropTraderBehavior().to_dict(),
    "retail": RetailBehavior().to_dict(),
    "market_maker": MarketMakerBehavior().to_dict(),
}


def get_default_behavior(category: AgentCategory) -> dict:
    """Get default behavior parameters for an agent category."""
    return DEFAULT_BEHAVIORS[category].copy()


def merge_behavior_params(
    category: AgentCategory,
    overrides: dict | None = None
) -> dict:
    """
    Merge default parameters with custom overrides.

    Args:
        category: Agent category
        overrides: Custom parameter overrides

    Returns:
        Merged parameter dictionary
    """
    params = get_default_behavior(category)
    if overrides:
        params.update(overrides)
    return params


__all__ = [
    "AgentCategory",
    "InstitutionalBehavior",
    "PropTraderBehavior",
    "RetailBehavior",
    "MarketMakerBehavior",
    "DEFAULT_BEHAVIORS",
    "get_default_behavior",
    "merge_behavior_params",
]

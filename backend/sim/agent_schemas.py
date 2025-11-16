"""
Pydantic schemas for agent behavior configuration API (T064).

Feature: 001-ai-user-order-matching, Phase 5, US2
"""
from pydantic import BaseModel, Field
from typing import Literal


AgentCategory = Literal["institutional", "prop", "retail", "market_maker"]


class BehaviorConfig(BaseModel):
    """Behavior configuration for an agent."""

    behavior_category: AgentCategory = Field(
        ..., description="Agent behavior type"
    )
    profit_target: float = Field(
        ge=0.0, le=1.0, description="Target profit percentage (0-1)"
    )
    stop_loss: float = Field(
        ge=0.0, le=1.0, description="Stop-loss threshold percentage (0-1)"
    )
    herd_behavior_strength: float = Field(
        ge=0.0, le=1.0, description="Tendency to follow market momentum (0-1)"
    )
    momentum_sensitivity: float = Field(
        ge=0.0, le=1.0, description="Sensitivity to price momentum signals (0-1)"
    )
    risk_tolerance: float = Field(
        ge=0.0, le=1.0, description="Risk appetite (0-1)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "behavior_category": "retail",
                "profit_target": 0.30,
                "stop_loss": 0.20,
                "herd_behavior_strength": 0.75,
                "momentum_sensitivity": 0.60,
                "risk_tolerance": 0.55,
            }
        }


class UpdateAgentBehaviorRequest(BaseModel):
    """Request to update agent behavior parameters."""

    participant_code: str = Field(..., description="Participant code (e.g., 'retail-agent')")
    behavior_config: BehaviorConfig


class AgentBehaviorResponse(BaseModel):
    """Response containing agent behavior configuration."""

    participant_code: str
    behavior_config: BehaviorConfig
    updated: bool = Field(
        description="Whether the configuration was updated (vs. fetched)"
    )


class ListAgentBehaviorsResponse(BaseModel):
    """Response listing all agents and their behaviors in a session."""

    session_id: int
    agents: list[dict]  # List of {participant_code, behavior_category, ...}


class AgentDetail(BaseModel):
    """T075: Detailed agent information including behavior parameters."""

    participant_code: str
    participant_type: str
    behavior_category: AgentCategory | None = None
    profit_target: float | None = None
    stop_loss: float | None = None
    herd_behavior_strength: float | None = None
    momentum_sensitivity: float | None = None
    risk_tolerance: float | None = None
    avg_position_cost: float | None = None
    score: float = 0.0
    created_at: str
    updated_at: str


class AgentListResponse(BaseModel):
    """T075: Response for GET /sessions/{session_id}/agents."""

    session_id: int
    total: int
    agents: list[AgentDetail]


class AgentPerformance(BaseModel):
    """T078: Agent performance metrics."""

    participant_code: str
    total_orders: int = 0
    total_trades: int = 0
    total_volume: float = 0.0
    avg_trade_size: float = 0.0
    win_rate: float | None = None
    profit_loss_pct: float | None = None
    sharpe_ratio: float | None = None


class AgentPerformanceResponse(BaseModel):
    """T078: Response for GET /sessions/{session_id}/agents/{agent_id}/performance."""

    session_id: int
    participant_code: str
    performance: AgentPerformance


class AgentPoolStats(BaseModel):
    """T079: Statistics for an agent pool (e.g., all retail agents)."""

    pool_code: str
    agent_count: int
    total_orders: int
    total_trades: int
    total_volume: float
    avg_behavior_params: dict  # Average of all behavior parameters in pool


class AgentPoolListResponse(BaseModel):
    """T079: Response for GET /sessions/{session_id}/pools."""

    session_id: int
    pools: list[AgentPoolStats]


class AgentPoolDetailResponse(BaseModel):
    """T080: Response for GET /sessions/{session_id}/pools/{pool_code}/stats."""

    session_id: int
    pool_code: str
    stats: AgentPoolStats
    agents: list[AgentDetail]  # All agents in this pool


class UpdateAgentConfigRequest(BaseModel):
    """T077: Request to update agent configuration."""

    behavior_category: AgentCategory | None = None
    profit_target: float | None = Field(None, ge=0.0, le=1.0)
    stop_loss: float | None = Field(None, ge=0.0, le=1.0)
    herd_behavior_strength: float | None = Field(None, ge=0.0, le=1.0)
    momentum_sensitivity: float | None = Field(None, ge=0.0, le=1.0)
    risk_tolerance: float | None = Field(None, ge=0.0, le=1.0)


class UpdateAgentConfigResponse(BaseModel):
    """T077: Response for PUT /sessions/{session_id}/agents/{agent_id}/config."""

    session_id: int
    participant_code: str
    updated: bool
    config: AgentDetail


__all__ = [
    "AgentCategory",
    "BehaviorConfig",
    "UpdateAgentBehaviorRequest",
    "AgentBehaviorResponse",
    "ListAgentBehaviorsResponse",
    "AgentDetail",
    "AgentListResponse",
    "AgentPerformance",
    "AgentPerformanceResponse",
    "AgentPoolStats",
    "AgentPoolListResponse",
    "AgentPoolDetailResponse",
    "UpdateAgentConfigRequest",
    "UpdateAgentConfigResponse",
]

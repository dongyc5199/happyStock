from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class SimulationStartRequest(BaseModel):
    session_code: str = Field(..., min_length=1, description="Session code used for Redis namespace")
    mode: str = Field("auto", description="Simulation mode identifier")
    tick_interval_ms: int = Field(1000, ge=100, le=60000, description="Tick interval in milliseconds")
    total_ticks: int = Field(0, ge=0, description="Planned total ticks")
    config_version: Optional[str] = Field(None, description="Config version identifier")

class SimulationStartResponse(BaseModel):
    session_id: int
    session_code: str
    tick_interval_ms: int
    total_ticks: int
    status: str = Field("accepted", description="Processing status (accepted/duplicate/error)")
    trace_id: str = Field(..., description="Trace identifier for tracking asynchronous processing")
    created_at: datetime

import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app


def start_session(client: TestClient, payload: dict) -> dict:
    response = client.post("/api/sim/start", json=payload)
    if response.status_code == 503:
        pytest.skip("Simulation database unavailable")
    assert response.status_code == 202, response.text
    return response.json()


def step_session(client: TestClient, payload: dict):
    return client.post("/api/sim/step", json=payload)


def test_simulation_start_step_flow():
    start_payload = {
        "session_code": f"flow-{uuid.uuid4().hex[:24]}",
        "mode": "auto",
        "tick_interval_ms": 500,
        "total_ticks": 5,
    }

    with TestClient(app) as client:
        session = start_session(client, start_payload)
        tick_payload = {
            "session_id": session["session_id"],
            "session_code": session["session_code"],
            "tick": 1,
            "orders": [
                {
                    "order_id": "flow-order-1",
                    "participant_id": "player-1",
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": 3,
                }
            ],
        }
        step_response = step_session(client, tick_payload)
        assert step_response.status_code == 202, step_response.text
        body = step_response.json()
        assert "trace_id" in body
        assert "orders" in body
        assert "trades" in body
        assert "snapshot" in body

        state_resp = client.get(
            "/api/sim/state", params={"session_id": session["session_id"]}
        )
        assert state_resp.status_code == 200
        state_body = state_resp.json()
        if state_body:
            first = state_body[0]
            assert "features" in first
            assert "emotion" in first

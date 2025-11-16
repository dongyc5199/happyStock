# AI Agent Auto-Registration Integration Guide

## Overview

AI agents are now **automatically registered** for autoplay simulation sessions when the backend server starts. This eliminates the need for manual agent registration and ensures consistent agent behavior across sessions.

## How It Works

### 1. Startup Flow

When the backend server starts:

```
Backend Startup
  ↓
Initialize AgentRegistry (if SIM_AGENTS_ENABLED=true)
  ↓
Create SimulationAutoRunner with agent_registry
  ↓
AutoRunner starts and calls _ensure_sessions()
  ↓
For each configured session (e.g., autoplay-demo):
  - Check if session exists in database
  - If NOT exists: Create new session
  - If newly created: Call _register_default_agents()
  ↓
_register_default_agents() registers 10 AI agents:
  - 3 Prop Traders (aggressive, balanced, conservative)
  - 2 Institutional Investors (large, medium)
  - 5 Retail Traders (2 followers, 2 moderate, 1 independent)
  ↓
Agents begin trading on next tick
```

### 2. Agent Configuration

The default agent configuration is defined in `backend/sim/auto_runner.py`:

#### Prop Traders (游资交易者)

| Agent Code | Base Qty | Profit Target | Stop Loss | Risk Tolerance | Weight |
|------------|----------|---------------|-----------|----------------|--------|
| `prop-aggressive` | 120.0 | 5% | 2% | 0.9 | 1.2 |
| `prop-balanced` | 100.0 | 3% | 1.5% | 0.7 | 1.0 |
| `prop-conservative` | 80.0 | 2% | 1% | 0.5 | 0.8 |

**Behavior**: Momentum-based trading with profit targets and stop losses.

#### Institutional Investors (机构交易者)

| Agent Code | Base Qty | Mean Rev. Window | Rebalance Threshold | TWAP Enabled | Weight |
|------------|----------|------------------|---------------------|--------------|--------|
| `inst-large` | 200.0 | 100 ticks | 2% | Yes (max 150) | 1.5 |
| `inst-medium` | 100.0 | 50 ticks | 3% | Yes (max 100) | 1.0 |

**Behavior**: Mean reversion strategy with TWAP order splitting for large orders.

#### Retail Traders (散户交易者)

| Agent Code | Base Qty | Herd Strength | Momentum Sens. | Weight |
|------------|----------|---------------|----------------|--------|
| `retail-follower-1` | 30.0 | 0.9 | 0.8 | 0.6 |
| `retail-follower-2` | 30.0 | 0.9 | 0.8 | 0.6 |
| `retail-moderate-1` | 40.0 | 0.5 | 0.6 | 0.8 |
| `retail-moderate-2` | 40.0 | 0.5 | 0.6 | 0.8 |
| `retail-independent` | 50.0 | 0.2 | 0.4 | 1.0 |

**Behavior**: Sentiment-following with varying herd behavior strength.

### 3. Configuration Requirements

To enable AI agent auto-registration, ensure the following settings in `backend/.env`:

```bash
# Required: Enable AI agents
SIM_AGENTS_ENABLED=true

# Required: Configure autoplay sessions
SIM_AUTOPLAY_SESSIONS=["autoplay-demo"]

# Optional: Configure session-specific profiles
# (Agents will be registered for all sessions in SIM_AUTOPLAY_SESSIONS)
```

## Verification

### 1. Check Startup Logs

When the backend starts, you should see:

```
[+] Simulation agent registry ready
[+] Simulation autoplay runner enabled (1 sessions)
INFO:     Registering AI agents for session: autoplay-demo (ID: 1)
INFO:     Successfully registered 10 AI agents for session autoplay-demo (3 prop, 2 institutional, 5 retail)
```

### 2. Use the API to List Agents

```bash
# Get session ID first
curl http://localhost:8000/api/sim/sessions

# List agents for the session
curl http://localhost:8000/api/sim/sessions/{session_id}/agents
```

Expected response:

```json
{
  "success": true,
  "agents": [
    {
      "participant_code": "prop-aggressive",
      "participant_type": "agent",
      "behavior_category": "prop_momentum",
      "profit_target": 0.05,
      "stop_loss": 0.02,
      ...
    },
    ...
  ]
}
```

### 3. Run the Test Script

```bash
cd backend
pipenv run python scripts/test_agent_auto_registration.py
```

This script simulates the auto-registration logic and verifies it works correctly.

## Manual Agent Registration (Advanced)

If you need to manually register agents for existing sessions, use:

```bash
cd backend
pipenv run python scripts/register_agents_for_session.py [session_code]

# Example:
pipenv run python scripts/register_agents_for_session.py autoplay-demo
```

**Note**: Manually registered agents are **in-memory only** and will be lost on server restart. The auto-registration logic handles this automatically.

## Customizing Agent Configuration

To customize the default agents, edit the `_register_default_agents()` method in `backend/sim/auto_runner.py`:

```python
async def _register_default_agents(self, session_id: int, session_code: str) -> None:
    """Register default AI agents for a newly created session."""
    # Modify agent parameters here
    await self._agent_registry.register(
        session_id=session_id,
        agent=PropMomentumAgent(
            code="my-custom-agent",
            base_quantity=150.0,
            profit_target=0.04,  # 4% profit target
            stop_loss=0.02,      # 2% stop loss
            risk_tolerance=0.8,
            momentum_sensitivity=0.9,
        ),
        weight=1.5,
        pool_code="prop",
    )
```

After making changes, restart the backend server.

## Agent Management API

### List All Agents

```http
GET /api/sim/sessions/{session_id}/agents
```

### Get Agent Details

```http
GET /api/sim/sessions/{session_id}/agents/{agent_code}
```

### Update Agent Configuration

```http
PUT /api/sim/sessions/{session_id}/agents/{agent_code}/config
Content-Type: application/json

{
  "profit_target": 0.04,
  "stop_loss": 0.015,
  "risk_tolerance": 0.85
}
```

### Get Agent Performance

```http
GET /api/sim/sessions/{session_id}/agents/{agent_code}/performance
```

### Get Pool Statistics

```http
GET /api/sim/sessions/{session_id}/pools/{pool_code}/stats
```

Available pools: `prop`, `institutional`, `retail`

## Troubleshooting

### Agents Not Appearing

1. **Check if agents are enabled**:
   ```bash
   cd backend
   pipenv run python scripts/check_agent_integration.py
   ```

2. **Check startup logs** for errors:
   - Look for: `[ERROR] Failed to register AI agents`
   - Check database connection issues

3. **Verify session exists**:
   ```bash
   curl http://localhost:8000/api/sim/sessions
   ```

### Agents Not Trading

1. **Verify agents are registered**:
   ```bash
   curl http://localhost:8000/api/sim/sessions/{session_id}/agents
   ```

2. **Check agent logs** (if enabled):
   ```bash
   # Check backend/logs/agent_*.log
   ```

3. **Monitor tick processing**:
   - Agents only generate orders during tick processing
   - Check if autoplay runner is active
   - Verify `SIM_AUTOPLAY_INTERVAL_MS` is reasonable (default: 500ms)

### Performance Issues

If many agents cause performance issues:

1. **Reduce agent count** in `_register_default_agents()`
2. **Increase tick interval**: Set `SIM_AUTOPLAY_INTERVAL_MS` to higher value (e.g., 1000ms)
3. **Disable verbose logging**: Set `SIM_AUTOPLAY_VERBOSE=false`

## Architecture Details

### In-Memory Storage

Agents are stored **in-memory** in the `AgentRegistry`:

```python
class AgentRegistry:
    def __init__(self):
        self._agents: Dict[int, List[RegisteredAgent]] = {}
        # Key: session_id
        # Value: List of registered agents
```

**Implications**:
- Fast access (no database queries)
- Agents persist for server lifetime
- Restart = agents re-registered automatically
- No persistence across server restarts (by design)

### Database Persistence

Agent **behavior parameters** and **performance metrics** ARE persisted in PostgreSQL:

- `simulation.participants` table stores agent metadata
- `simulation.orders` and `simulation.trades` store agent activity
- Agent statistics calculated from historical data

This allows:
- Historical analysis of agent behavior
- Performance tracking across server restarts
- Behavioral parameter evolution over time

## Future Enhancements

Potential improvements (not yet implemented):

1. **Dynamic Agent Adjustment**: Automatically adjust agent parameters based on market conditions
2. **Agent Pool Balancing**: Ensure balanced representation of agent types
3. **Custom Agent Profiles**: Load agent configurations from database or config files
4. **Agent Lifecycle Management**: Enable/disable agents dynamically via API
5. **Agent Learning**: Use reinforcement learning to evolve agent strategies

## Related Files

- `backend/sim/auto_runner.py` - Auto-registration logic
- `backend/sim/agents/registry.py` - AgentRegistry implementation
- `backend/sim/agents/prop.py` - PropMomentumAgent
- `backend/sim/agents/institutional.py` - InstitutionalRebalanceAgent
- `backend/sim/agents/retail.py` - RetailSentimentAgent
- `backend/routers/simulate.py` - Agent management API endpoints
- `backend/scripts/register_agents_for_session.py` - Manual registration script
- `backend/scripts/check_agent_integration.py` - Integration diagnostic script
- `backend/scripts/test_agent_auto_registration.py` - Auto-registration test script

## Summary

✅ **AI agents are now fully integrated** into the simulation system
✅ **Automatic registration** on backend startup for autoplay sessions
✅ **10 default agents** with differentiated behaviors
✅ **Complete API** for agent management and monitoring
✅ **Tested and verified** through comprehensive test suite

The autoplay-demo session (and any other configured autoplay sessions) will now have active AI agents trading automatically as soon as the backend server starts.

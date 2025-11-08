-- Migration: 0001_initial
-- Purpose : Create core simulation tables and hypertables

BEGIN;

CREATE TABLE IF NOT EXISTS simulation_session (
    id BIGSERIAL PRIMARY KEY,
    session_code VARCHAR(36) UNIQUE NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    mode VARCHAR(32) NOT NULL,
    tick_interval_ms INTEGER NOT NULL DEFAULT 1000,
    current_tick BIGINT NOT NULL DEFAULT 0,
    total_ticks BIGINT NOT NULL DEFAULT 0,
    config_version VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS agent_profile (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    display_name VARCHAR(64) NOT NULL,
    category VARCHAR(32) NOT NULL,
    weight NUMERIC(6,3) NOT NULL DEFAULT 1.0,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    risk_limits JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_participant (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES simulation_session(id) ON DELETE CASCADE,
    participant_type VARCHAR(16) NOT NULL,
    player_id UUID,
    agent_profile_id BIGINT REFERENCES agent_profile(id),
    influence_weight NUMERIC(10,4) NOT NULL DEFAULT 1.0,
    cash_balance NUMERIC(18,4) NOT NULL DEFAULT 0,
    inventory NUMERIC(18,4) NOT NULL DEFAULT 0,
    score NUMERIC(18,4) NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_participant_session
    ON session_participant (session_id, participant_type);

CREATE TABLE IF NOT EXISTS order_event (
    session_id BIGINT NOT NULL,
    tick BIGINT NOT NULL,
    order_id BIGSERIAL,
    participant_id BIGINT NOT NULL REFERENCES session_participant(id) ON DELETE CASCADE,
    side VARCHAR(4) NOT NULL,
    order_type VARCHAR(16) NOT NULL,
    price NUMERIC(18,4),
    quantity NUMERIC(18,4) NOT NULL,
    remaining_qty NUMERIC(18,4) NOT NULL,
    status VARCHAR(16) NOT NULL,
    impact NUMERIC(18,6),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, tick, created_at, order_id)
);

SELECT create_hypertable('order_event', by_range('created_at'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_order_event_session_tick
    ON order_event (session_id, tick);
CREATE INDEX IF NOT EXISTS idx_order_event_participant
    ON order_event (participant_id);

CREATE TABLE IF NOT EXISTS trade_event (
    session_id BIGINT NOT NULL,
    tick BIGINT NOT NULL,
    trade_id BIGSERIAL,
    buy_order_id BIGINT,
    sell_order_id BIGINT,
    price NUMERIC(18,4) NOT NULL,
    quantity NUMERIC(18,4) NOT NULL,
    impact NUMERIC(18,6),
    buyer_participant_id BIGINT REFERENCES session_participant(id),
    seller_participant_id BIGINT REFERENCES session_participant(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, tick, created_at, trade_id)
);

SELECT create_hypertable('trade_event', by_range('created_at'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_trade_event_session_tick
    ON trade_event (session_id, tick);

CREATE TABLE IF NOT EXISTS market_state (
    session_id BIGINT NOT NULL,
    tick BIGINT NOT NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    best_bid NUMERIC(18,4),
    best_ask NUMERIC(18,4),
    last_price NUMERIC(18,4),
    vwap_price NUMERIC(18,4),
    total_volume NUMERIC(18,4),
    imbalance NUMERIC(18,6),
    sentiment_score NUMERIC(10,5),
    liquidity_level NUMERIC(10,5),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (session_id, tick, ts)
);

SELECT create_hypertable('market_state', by_range('ts'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_state_ts
    ON market_state (ts DESC);

CREATE TABLE IF NOT EXISTS agent_log (
    session_id BIGINT NOT NULL,
    tick BIGINT NOT NULL,
    participant_id BIGINT NOT NULL REFERENCES session_participant(id) ON DELETE CASCADE,
    event_type VARCHAR(32) NOT NULL,
    detail JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, tick, created_at, participant_id, event_type)
);

SELECT create_hypertable('agent_log', by_range('created_at'), migrate_data => TRUE, if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_agent_log_participant
    ON agent_log (participant_id, created_at DESC);

CREATE TABLE IF NOT EXISTS metric_snapshot (
    session_id BIGINT NOT NULL,
    tick BIGINT NOT NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(64) NOT NULL,
    metric_value NUMERIC(20,6) NOT NULL,
    dimension JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (session_id, tick, ts, metric_name)
);

SELECT create_hypertable('metric_snapshot', by_range('ts'), migrate_data => TRUE, if_not_exists => TRUE);

COMMIT;

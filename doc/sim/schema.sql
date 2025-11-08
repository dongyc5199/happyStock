-- 仿真后端核心表结构（TimescaleDB + PostgreSQL）
-- 执行前请确认已连接到仿真库：\c happystock_sim

BEGIN;

-- 1. 仿真会话
CREATE TABLE IF NOT EXISTS simulation_session (
    id              BIGSERIAL PRIMARY KEY,
    session_code    VARCHAR(36) UNIQUE NOT NULL, -- 便于对外暴露
    status          VARCHAR(16) NOT NULL DEFAULT 'pending', -- pending|running|paused|closed
    mode            VARCHAR(32) NOT NULL,       -- sandbox / live / playback
    tick_interval_ms INTEGER NOT NULL DEFAULT 1000,
    current_tick    BIGINT NOT NULL DEFAULT 0,
    total_ticks     BIGINT NOT NULL DEFAULT 0,
    config_version  VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_simulation_session_code
    ON simulation_session (session_code);

-- 2. 玩家/智能体配置
CREATE TABLE IF NOT EXISTS agent_profile (
    id            BIGSERIAL PRIMARY KEY,
    code          VARCHAR(32) UNIQUE NOT NULL,  -- e.g. RETAIL, PROP_DESK
    display_name  VARCHAR(64) NOT NULL,
    category      VARCHAR(32) NOT NULL,         -- retail / prop / institution / market_maker
    weight        NUMERIC(6,3) NOT NULL DEFAULT 1.0,
    parameters    JSONB NOT NULL DEFAULT '{}'::jsonb,
    risk_limits   JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. 会话参与者映射（玩家或智能体实例）
CREATE TABLE IF NOT EXISTS session_participant (
    id            BIGSERIAL PRIMARY KEY,
    session_id    BIGINT NOT NULL REFERENCES simulation_session(id) ON DELETE CASCADE,
    participant_type VARCHAR(16) NOT NULL,      -- player / agent
    player_id     UUID,                         -- 真实玩家引用
    agent_profile_id BIGINT REFERENCES agent_profile(id),
    influence_weight NUMERIC(10,4) NOT NULL DEFAULT 1.0,
    cash_balance  NUMERIC(18,4) NOT NULL DEFAULT 0,
    inventory     NUMERIC(18,4) NOT NULL DEFAULT 0,
    score         NUMERIC(18,4) NOT NULL DEFAULT 0,
    metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_participant_session
    ON session_participant (session_id, participant_type);

-- 4. 订单簿（原始订单流，Timescale hypertable）
CREATE TABLE IF NOT EXISTS order_event (
    session_id     BIGINT NOT NULL,
    tick           BIGINT NOT NULL,
    order_id       BIGSERIAL,
    participant_id BIGINT NOT NULL REFERENCES session_participant(id) ON DELETE CASCADE,
    side           VARCHAR(4) NOT NULL,         -- buy / sell
    order_type     VARCHAR(16) NOT NULL,        -- market / limit / stop
    price          NUMERIC(18,4),
    quantity       NUMERIC(18,4) NOT NULL,
    remaining_qty  NUMERIC(18,4) NOT NULL,
    status         VARCHAR(16) NOT NULL,        -- open / filled / cancelled / rejected
    impact         NUMERIC(18,6),
    metadata       JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, tick, order_id)
);

SELECT create_hypertable('order_event', by_range('created_at'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_order_event_session_tick
    ON order_event (session_id, tick);
CREATE INDEX IF NOT EXISTS idx_order_event_participant
    ON order_event (participant_id);

-- 5. 成交记录
CREATE TABLE IF NOT EXISTS trade_event (
    session_id     BIGINT NOT NULL,
    tick           BIGINT NOT NULL,
    trade_id       BIGSERIAL,
    buy_order_id   BIGINT,
    sell_order_id  BIGINT,
    price          NUMERIC(18,4) NOT NULL,
    quantity       NUMERIC(18,4) NOT NULL,
    impact         NUMERIC(18,6),
    buyer_participant_id BIGINT REFERENCES session_participant(id),
    seller_participant_id BIGINT REFERENCES session_participant(id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, tick, trade_id)
);

SELECT create_hypertable('trade_event', by_range('created_at'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_trade_event_session_tick
    ON trade_event (session_id, tick);

-- 6. 行情快照（盘口、价格、情绪指标）
CREATE TABLE IF NOT EXISTS market_state (
    session_id     BIGINT NOT NULL,
    tick           BIGINT NOT NULL,
    ts             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    best_bid       NUMERIC(18,4),
    best_ask       NUMERIC(18,4),
    last_price     NUMERIC(18,4),
    vwap_price     NUMERIC(18,4),
    total_volume   NUMERIC(18,4),
    imbalance      NUMERIC(18,6),
    sentiment_score NUMERIC(10,5),
    liquidity_level NUMERIC(10,5),
    payload        JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (session_id, tick)
);

SELECT create_hypertable('market_state', by_range('ts'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_state_ts
    ON market_state (ts DESC);

-- 7. 玩家/智能体日志（AI 教练输入）
CREATE TABLE IF NOT EXISTS agent_log (
    session_id     BIGINT NOT NULL,
    tick           BIGINT NOT NULL,
    participant_id BIGINT NOT NULL REFERENCES session_participant(id) ON DELETE CASCADE,
    event_type     VARCHAR(32) NOT NULL,
    detail         JSONB NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, tick, participant_id, event_type)
);

SELECT create_hypertable('agent_log', by_range('created_at'), migrate_data => TRUE, if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_agent_log_participant
    ON agent_log (participant_id, created_at DESC);

-- 8. 指标快照（供监控与排行榜使用）
CREATE TABLE IF NOT EXISTS metric_snapshot (
    session_id     BIGINT NOT NULL,
    tick           BIGINT NOT NULL,
    ts             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name    VARCHAR(64) NOT NULL,
    metric_value   NUMERIC(20,6) NOT NULL,
    dimension      JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (session_id, tick, metric_name)
);

SELECT create_hypertable('metric_snapshot', by_range('ts'), migrate_data => TRUE, if_not_exists => TRUE);

COMMIT;

-- Hypertable chunk 策略示例（可选）
-- SELECT set_chunk_time_interval('order_event', INTERVAL '1 hour');
-- SELECT add_retention_policy('market_state', INTERVAL '30 days');

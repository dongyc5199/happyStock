-- Market data tables for mock data generation
-- Compatible with PostgreSQL (recommended) and MySQL (fallback)

-- 1. Market K-line data table (partitioned by month)
-- PostgreSQL version with native partitioning
CREATE TABLE IF NOT EXISTS market_klines (
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    time BIGINT NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, interval, time)
) PARTITION BY RANGE (time);

-- Create partitions for 2025-2026 (extend as needed)
-- Each partition covers one month (approximately 2.6M seconds)
CREATE TABLE market_klines_2025_01 PARTITION OF market_klines
    FOR VALUES FROM (1704067200) TO (1706745600);  -- 2025-01-01 to 2025-02-01

CREATE TABLE market_klines_2025_02 PARTITION OF market_klines
    FOR VALUES FROM (1706745600) TO (1709251200);  -- 2025-02-01 to 2025-03-01

CREATE TABLE market_klines_2025_03 PARTITION OF market_klines
    FOR VALUES FROM (1709251200) TO (1711929600);  -- 2025-03-01 to 2025-04-01

CREATE TABLE market_klines_2025_04 PARTITION OF market_klines
    FOR VALUES FROM (1711929600) TO (1714521600);  -- 2025-04-01 to 2025-05-01

CREATE TABLE market_klines_2025_05 PARTITION OF market_klines
    FOR VALUES FROM (1714521600) TO (1717200000);  -- 2025-05-01 to 2025-06-01

CREATE TABLE market_klines_2025_06 PARTITION OF market_klines
    FOR VALUES FROM (1717200000) TO (1719792000);  -- 2025-06-01 to 2025-07-01

CREATE TABLE market_klines_2025_07 PARTITION OF market_klines
    FOR VALUES FROM (1719792000) TO (1722470400);  -- 2025-07-01 to 2025-08-01

CREATE TABLE market_klines_2025_08 PARTITION OF market_klines
    FOR VALUES FROM (1722470400) TO (1725148800);  -- 2025-08-01 to 2025-09-01

CREATE TABLE market_klines_2025_09 PARTITION OF market_klines
    FOR VALUES FROM (1725148800) TO (1727740800);  -- 2025-09-01 to 2025-10-01

CREATE TABLE market_klines_2025_10 PARTITION OF market_klines
    FOR VALUES FROM (1727740800) TO (1730419200);  -- 2025-10-01 to 2025-11-01

CREATE TABLE market_klines_2025_11 PARTITION OF market_klines
    FOR VALUES FROM (1730419200) TO (1733011200);  -- 2025-11-01 to 2025-12-01

CREATE TABLE market_klines_2025_12 PARTITION OF market_klines
    FOR VALUES FROM (1733011200) TO (1735689600);  -- 2025-12-01 to 2026-01-01

-- Covering index for efficient queries (avoids table lookups)
CREATE INDEX idx_market_klines_symbol_interval_time
    ON market_klines (symbol, interval, time DESC)
    INCLUDE (open, high, low, close, volume);

-- Index for time-range queries
CREATE INDEX idx_market_klines_time ON market_klines (time DESC);

-- 2. Stock state table (tracks current price and market state)
CREATE TABLE IF NOT EXISTS stock_state (
    symbol VARCHAR(20) PRIMARY KEY,
    current_price NUMERIC(10, 2) NOT NULL,
    volatility NUMERIC(6, 4) NOT NULL DEFAULT 0.02,
    trend NUMERIC(6, 4) NOT NULL DEFAULT 0.0,
    market_state VARCHAR(20) NOT NULL DEFAULT 'sideways',  -- bull, bear, sideways
    last_update BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Market status table (tracks trading hours and system status)
CREATE TABLE IF NOT EXISTS market_status (
    id SERIAL PRIMARY KEY,
    is_trading BOOLEAN NOT NULL DEFAULT FALSE,
    current_session VARCHAR(20),  -- morning, afternoon, closed
    session_start BIGINT,
    session_end BIGINT,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial market status
INSERT INTO market_status (is_trading, current_session)
VALUES (FALSE, 'closed')
ON CONFLICT DO NOTHING;

-- 4. Realtime price cache table (UNLOGGED for performance)
CREATE UNLOGGED TABLE IF NOT EXISTS stock_realtime_price (
    symbol VARCHAR(20) PRIMARY KEY,
    current_price NUMERIC(10, 2) NOT NULL,
    change_percent NUMERIC(6, 3),
    volume BIGINT,
    last_update BIGINT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Stock metadata table (static stock information)
CREATE TABLE IF NOT EXISTS stock_metadata (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(50),
    base_price NUMERIC(10, 2) NOT NULL,  -- Starting price
    base_volatility NUMERIC(6, 4) DEFAULT 0.02,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial test stocks
INSERT INTO stock_metadata (symbol, name, sector, base_price, base_volatility, is_active)
VALUES
    ('AAPL', 'Apple Inc.', 'Technology', 150.00, 0.025, TRUE),
    ('TSLA', 'Tesla Inc.', 'Automotive', 200.00, 0.035, TRUE),
    ('MSFT', 'Microsoft Corporation', 'Technology', 300.00, 0.020, TRUE),
    ('AMZN', 'Amazon.com Inc.', 'E-commerce', 130.00, 0.028, TRUE),
    ('GOOGL', 'Alphabet Inc.', 'Technology', 140.00, 0.022, TRUE),
    ('META', 'Meta Platforms Inc.', 'Technology', 350.00, 0.030, TRUE),
    ('NVDA', 'NVIDIA Corporation', 'Technology', 450.00, 0.032, TRUE),
    ('BRK.B', 'Berkshire Hathaway Inc.', 'Finance', 380.00, 0.015, TRUE),
    ('JPM', 'JPMorgan Chase & Co.', 'Finance', 160.00, 0.018, TRUE),
    ('V', 'Visa Inc.', 'Finance', 250.00, 0.020, TRUE)
ON CONFLICT (symbol) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE market_klines IS 'Partitioned K-line data for all intervals';
COMMENT ON TABLE stock_state IS 'Current state and parameters for each stock';
COMMENT ON TABLE market_status IS 'Global market trading status';
COMMENT ON TABLE stock_realtime_price IS 'High-performance realtime price cache';
COMMENT ON TABLE stock_metadata IS 'Static stock information';

-- Migration 0004: User Orders
-- Feature: 001-ai-user-order-matching
-- Purpose: Create user_orders table for tracking user-submitted orders
-- Dependencies: Requires sim_sessions and users tables

-- Create user_orders table
CREATE TABLE IF NOT EXISTS user_orders (
    order_id VARCHAR(64) PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES simulation_session(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,  -- FK to users table (assumed to exist)
    participant_id VARCHAR(64) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type VARCHAR(6) NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT')),
    quantity DECIMAL(18,6) NOT NULL CHECK (quantity > 0),
    price DECIMAL(18,4),
    timestamp BIGINT NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('PENDING', 'NEW', 'PARTIAL', 'FILLED', 'CANCELLED')),
    filled_quantity DECIMAL(18,6) NOT NULL DEFAULT 0 CHECK (filled_quantity >= 0),
    avg_filled_price DECIMAL(18,4),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_user_orders_session_user ON user_orders(session_id, user_id);
CREATE INDEX IF NOT EXISTS idx_user_orders_status ON user_orders(status) WHERE status IN ('PENDING', 'NEW', 'PARTIAL');
CREATE INDEX IF NOT EXISTS idx_user_orders_timestamp ON user_orders(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_orders_created_at ON user_orders(created_at DESC);

-- Add comment for documentation
COMMENT ON TABLE user_orders IS 'User-submitted trading orders for simulation sessions';
COMMENT ON COLUMN user_orders.order_id IS 'Unique order identifier, format: user-{user_id}-{timestamp}-{random}';
COMMENT ON COLUMN user_orders.participant_id IS 'Matching engine participant ID, format: user-{user_id}';
COMMENT ON COLUMN user_orders.timestamp IS 'Order submission timestamp in nanoseconds (int64)';
COMMENT ON COLUMN user_orders.status IS 'Order lifecycle status: PENDING (queued) → NEW (in matching) → PARTIAL (partially filled) → FILLED (complete) or CANCELLED';
COMMENT ON COLUMN user_orders.filled_quantity IS 'Cumulative filled quantity, must be <= quantity';

-- Create trigger for updated_at auto-update
CREATE OR REPLACE FUNCTION update_user_orders_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_orders_updated_at_trigger
    BEFORE UPDATE ON user_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_user_orders_updated_at();

-- Validation: Ensure LIMIT orders have price
ALTER TABLE user_orders ADD CONSTRAINT chk_limit_order_price
    CHECK (order_type != 'LIMIT' OR price IS NOT NULL);

-- Validation: Ensure filled_quantity never exceeds quantity
ALTER TABLE user_orders ADD CONSTRAINT chk_filled_quantity_valid
    CHECK (filled_quantity <= quantity);

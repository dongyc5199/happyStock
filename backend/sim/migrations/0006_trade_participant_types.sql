-- Migration 0006: Trade Participant Types
-- Feature: 001-ai-user-order-matching
-- Purpose: Add buyer/seller type tracking to identify user vs AI agent trades
-- Dependencies: Requires trade_event table

-- Add participant type columns to trade_event
ALTER TABLE trade_event
ADD COLUMN IF NOT EXISTS buyer_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS seller_type VARCHAR(20);

-- Add check constraints for valid participant types
ALTER TABLE trade_event
ADD CONSTRAINT chk_buyer_type_valid
    CHECK (buyer_type IN ('user', 'ai_retail', 'ai_prop', 'ai_institutional', 'ai_market_maker') OR buyer_type IS NULL);

ALTER TABLE trade_event
ADD CONSTRAINT chk_seller_type_valid
    CHECK (seller_type IN ('user', 'ai_retail', 'ai_prop', 'ai_institutional', 'ai_market_maker') OR seller_type IS NULL);

-- Create indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_trade_event_buyer_type ON trade_event(buyer_type);
CREATE INDEX IF NOT EXISTS idx_trade_event_seller_type ON trade_event(seller_type);
CREATE INDEX IF NOT EXISTS idx_trade_event_participant_types ON trade_event(buyer_type, seller_type);

-- Add comments for documentation
COMMENT ON COLUMN trade_event.buyer_type IS 'Type of buyer: user (real user), ai_retail, ai_prop, ai_institutional, ai_market_maker';
COMMENT ON COLUMN trade_event.seller_type IS 'Type of seller: user (real user), ai_retail, ai_prop, ai_institutional, ai_market_maker';

-- Backfill existing trades with ai_retail default (since historical trades are all AI)
-- This is safe because no user trades exist yet before this migration
UPDATE trade_event
SET buyer_type = COALESCE(buyer_type, 'ai_retail'),
    seller_type = COALESCE(seller_type, 'ai_retail')
WHERE buyer_type IS NULL OR seller_type IS NULL;

-- Make columns NOT NULL after backfill (future trades must specify participant types)
ALTER TABLE trade_event
ALTER COLUMN buyer_type SET NOT NULL,
ALTER COLUMN seller_type SET NOT NULL;

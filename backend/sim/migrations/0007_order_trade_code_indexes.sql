-- Migration: 0007_order_trade_code_indexes
-- Purpose : Add indexes on *_participant_code columns for order/trade events
--           to optimize analytics queries related to orderbook activity.

BEGIN;

-- Support queries like:
-- SELECT COUNT(*), SUM(quantity)
--   FROM order_event
--  WHERE session_id = $1 AND participant_code = $2;
CREATE INDEX IF NOT EXISTS idx_order_event_session_participant_code
    ON order_event (session_id, participant_code);

-- Support queries like:
-- SELECT COUNT(*), SUM(quantity)
--   FROM trade_event
--  WHERE session_id = $1
--    AND (buyer_participant_code = $2 OR seller_participant_code = $2);
CREATE INDEX IF NOT EXISTS idx_trade_event_session_buyer_code
    ON trade_event (session_id, buyer_participant_code);

CREATE INDEX IF NOT EXISTS idx_trade_event_session_seller_code
    ON trade_event (session_id, seller_participant_code);

COMMIT;


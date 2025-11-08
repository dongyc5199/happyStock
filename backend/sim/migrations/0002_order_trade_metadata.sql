-- Migration: 0002_order_trade_metadata
-- Purpose: add columns for external order codes/participants on order_event/trade_event

BEGIN;

ALTER TABLE order_event
    ADD COLUMN order_code VARCHAR(64),
    ADD COLUMN participant_code VARCHAR(64);

ALTER TABLE trade_event
    ADD COLUMN buy_order_code VARCHAR(64),
    ADD COLUMN sell_order_code VARCHAR(64),
    ADD COLUMN buyer_participant_code VARCHAR(64),
    ADD COLUMN seller_participant_code VARCHAR(64);

COMMIT;


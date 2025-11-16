-- Migration 0005: Agent Behavior Parameters
-- Feature: 001-ai-user-order-matching
-- Purpose: Add behavioral differentiation fields to AI agents
-- Dependencies: Requires session_participant table from 0001_initial.sql

-- Add behavior configuration columns to session_participant
ALTER TABLE session_participant
ADD COLUMN IF NOT EXISTS behavior_category VARCHAR(20) CHECK (behavior_category IN ('institutional', 'prop', 'retail', 'market_maker')),
ADD COLUMN IF NOT EXISTS profit_target DECIMAL(5,4) DEFAULT 0.03 CHECK (profit_target >= 0 AND profit_target <= 1),
ADD COLUMN IF NOT EXISTS stop_loss DECIMAL(5,4) DEFAULT 0.015 CHECK (stop_loss >= 0 AND stop_loss <= 1),
ADD COLUMN IF NOT EXISTS herd_behavior_strength DECIMAL(3,2) DEFAULT 0.0 CHECK (herd_behavior_strength >= 0 AND herd_behavior_strength <= 1),
ADD COLUMN IF NOT EXISTS momentum_sensitivity DECIMAL(3,2) DEFAULT 0.5 CHECK (momentum_sensitivity >= 0 AND momentum_sensitivity <= 1),
ADD COLUMN IF NOT EXISTS risk_tolerance DECIMAL(3,2) DEFAULT 0.5 CHECK (risk_tolerance >= 0 AND risk_tolerance <= 1),
ADD COLUMN IF NOT EXISTS avg_position_cost DECIMAL(18,4);

-- Create index for behavior category filtering
CREATE INDEX IF NOT EXISTS idx_participants_behavior_category ON session_participant(behavior_category);

-- Add comments for documentation
COMMENT ON COLUMN session_participant.behavior_category IS 'Agent behavior type: institutional (value), prop (momentum), retail (herd), market_maker (spread)';
COMMENT ON COLUMN session_participant.profit_target IS 'Target profit percentage (0-1) before taking profits, e.g., 0.03 = 3%';
COMMENT ON COLUMN session_participant.stop_loss IS 'Stop-loss threshold percentage (0-1), e.g., 0.015 = 1.5%';
COMMENT ON COLUMN session_participant.herd_behavior_strength IS 'Tendency to follow market momentum (0-1), higher for retail agents';
COMMENT ON COLUMN session_participant.momentum_sensitivity IS 'Sensitivity to price momentum signals (0-1), higher for prop traders';
COMMENT ON COLUMN session_participant.risk_tolerance IS 'Risk appetite (0-1), affects position sizing and order aggressiveness';
COMMENT ON COLUMN session_participant.avg_position_cost IS 'Average cost basis for current position, used for P&L calculation';

-- Update existing agents with default behavior categories based on participant_type patterns
-- This is a one-time migration to classify existing agents
UPDATE session_participant
SET behavior_category = CASE
    WHEN participant_code LIKE '%retail%' THEN 'retail'
    WHEN participant_code LIKE '%prop%' THEN 'prop'
    WHEN participant_code LIKE '%inst%' THEN 'institutional'
    WHEN participant_code LIKE '%maker%' THEN 'market_maker'
    ELSE 'retail' -- Default to retail for unclassified agents
END
WHERE behavior_category IS NULL;

-- Set behavior-specific defaults for existing agents
UPDATE session_participant
SET
    profit_target = CASE behavior_category
        WHEN 'retail' THEN 0.05
        WHEN 'prop' THEN 0.03
        WHEN 'institutional' THEN 0.02
        ELSE 0.03
    END,
    stop_loss = CASE behavior_category
        WHEN 'retail' THEN 0.02
        WHEN 'prop' THEN 0.015
        WHEN 'institutional' THEN 0.01
        ELSE 0.015
    END,
    herd_behavior_strength = CASE behavior_category
        WHEN 'retail' THEN 0.70
        WHEN 'prop' THEN 0.20
        WHEN 'institutional' THEN 0.05
        WHEN 'market_maker' THEN 0.00
        ELSE 0.00
    END,
    momentum_sensitivity = CASE behavior_category
        WHEN 'retail' THEN 0.30
        WHEN 'prop' THEN 0.60
        WHEN 'institutional' THEN 0.20
        WHEN 'market_maker' THEN 0.00
        ELSE 0.50
    END,
    risk_tolerance = CASE behavior_category
        WHEN 'retail' THEN 0.60
        WHEN 'prop' THEN 0.80
        WHEN 'institutional' THEN 0.40
        WHEN 'market_maker' THEN 0.30
        ELSE 0.50
    END
WHERE profit_target = 0.03 AND stop_loss = 0.015; -- Only update if still at defaults

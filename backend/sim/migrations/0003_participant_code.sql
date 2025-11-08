-- Migration: 0003_participant_code
-- Purpose : add participant_code column for session participants and provide uniqueness per session

BEGIN;

ALTER TABLE session_participant
    ADD COLUMN IF NOT EXISTS participant_code VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS idx_session_participant_code
    ON session_participant (session_id, participant_code);

COMMIT;

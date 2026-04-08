-- Migration: Add is_locked column to arrsdata and eventsdata tables
-- Version: 004
-- Date: 2026-04-08

-- Add is_locked to arrsdata
ALTER TABLE arrsdata
ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE COMMENT 'Prevent sync overwrites when locked' AFTER updated_at;

CREATE INDEX IF NOT EXISTS idx_arrsdata_is_locked ON arrsdata(is_locked);

-- Add is_locked to eventsdata
ALTER TABLE eventsdata
ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE COMMENT 'Prevent sync overwrites when locked' AFTER updated_at;

CREATE INDEX IF NOT EXISTS idx_eventsdata_is_locked ON eventsdata(is_locked);

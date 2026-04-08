-- Migration: Move kulthash from eventsdata to arrsdata, add extra JSON to eventsdata
-- Version: 003
-- Date: 2026-04-08

-- 1. Add kulthash to arrsdata (hash of arrangement field values)
ALTER TABLE arrsdata
ADD COLUMN IF NOT EXISTS kulthash VARCHAR(32) NULL COMMENT 'MD5 hash of arrangement fields' AFTER tmdb;

-- 2. Add index for kulthash in arrsdata
CREATE INDEX IF NOT EXISTS idx_arrsdata_kulthash ON arrsdata(kulthash);

-- 3. Remove kulthash from eventsdata  (now only in arrsdata)
ALTER TABLE eventsdata
DROP COLUMN IF EXISTS kulthash;

-- 4. Add extra JSON field to eventsdata (for event-specific data)
ALTER TABLE eventsdata
ADD COLUMN IF NOT EXISTS extra JSON NULL COMMENT 'Event-specific data (e.g., extra notes, custom fields)' AFTER updated_at;

-- Verify tables
-- SELECT * FROM arrsdata LIMIT 1;
-- SELECT * FROM eventsdata LIMIT 1;

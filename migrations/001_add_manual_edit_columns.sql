-- Migration: Add manual edit tracking and lock support to kultevents table
-- Version: 001
-- Date: 2026-03-31

-- Add columns to kultevents table for manual edit tracking
ALTER TABLE kultevents 
ADD COLUMN IF NOT EXISTS is_manually_edited BOOLEAN DEFAULT FALSE AFTER kulthash,
ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE AFTER is_manually_edited,
ADD COLUMN IF NOT EXISTS manual_edit_timestamp DATETIME NULL AFTER is_locked;

-- Create audit history table for tracking manual edits
CREATE TABLE IF NOT EXISTS kultevents_edit_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ArrNr BIGINT NOT NULL,
  field_name VARCHAR(100) NOT NULL,
  old_value TEXT,
  new_value TEXT,
  edited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  edited_by VARCHAR(100) DEFAULT 'manual',
  FOREIGN KEY (ArrNr) REFERENCES kultevents(ArrNr) ON DELETE CASCADE,
  INDEX idx_arrnr (ArrNr),
  INDEX idx_edited_at (edited_at)
);

-- Add index for lock queries
CREATE INDEX IF NOT EXISTS idx_is_locked ON kultevents(is_locked);
CREATE INDEX IF NOT EXISTS idx_is_manually_edited ON kultevents(is_manually_edited);

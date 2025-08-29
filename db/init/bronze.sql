-- 1) Schema
CREATE SCHEMA IF NOT EXISTS bronze;

-- 2) Bronze table (one row per captured slice)
CREATE TABLE IF NOT EXISTS bronze.snapshots (
  id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source_type    TEXT        NOT NULL,   -- e.g., 'program_requirements'
  source_url     TEXT        NOT NULL,
  program_code   TEXT,                   -- e.g., 'BS-CS', 'BS-EE'
  subject_norm   TEXT,                   -- e.g., 'CS', 'EE'
  subject_raw    TEXT,                   -- e.g., 'C S', 'E E'
  catalog_year   TEXT,                   -- e.g., '2025-2026'
  group_name     TEXT,                   -- e.g., 'Major Requirements'
  term_id        TEXT,                   -- e.g., '202420' (ClassNav) else NULL
  captured_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  selector_used  TEXT,                   -- CSS/XPath you used
  content_hash   TEXT        NOT NULL,   -- hash of payload_html
  payload_html   TEXT        NOT NULL,   -- your exact <tbody>…</tbody> slice
  rows_json      JSONB,                  -- optional tiny per-row parse
  notes          TEXT
);

-- 3) Smart dedupe (saves headaches): prevents identical slices for same scope
CREATE UNIQUE INDEX IF NOT EXISTS snapshots_dedupe_uidx
ON bronze.snapshots (
  source_type,
  program_code,
  catalog_year,
  group_name,
  term_id,
  content_hash
) NULLS NOT DISTINCT;

-- 4) Fast lookup by scope + recency
CREATE INDEX IF NOT EXISTS snapshots_lookup_idx
ON bronze.snapshots (
  source_type, program_code, catalog_year, group_name, term_id, captured_at
);

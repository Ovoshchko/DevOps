-- Detector-centric operational schema

CREATE TABLE IF NOT EXISTS detector_profiles (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  status TEXT NOT NULL,
  sensitivity DOUBLE PRECISION NOT NULL,
  window_size_seconds INTEGER NOT NULL,
  window_step_seconds INTEGER NOT NULL,
  features JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS detection_runs (
  id TEXT PRIMARY KEY,
  detector_profile_id TEXT NOT NULL REFERENCES detector_profiles(id),
  window_start TIMESTAMPTZ NOT NULL,
  window_end TIMESTAMPTZ NOT NULL,
  initiated_by TEXT,
  status TEXT NOT NULL,
  summary JSONB,
  created_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS detection_results (
  id TEXT PRIMARY KEY,
  detection_run_id TEXT NOT NULL REFERENCES detection_runs(id),
  timestamp TIMESTAMPTZ NOT NULL,
  anomaly_score DOUBLE PRECISION NOT NULL,
  is_anomaly BOOLEAN NOT NULL,
  metrics_snapshot JSONB NOT NULL,
  explanation TEXT
);

CREATE TABLE IF NOT EXISTS generator_jobs (
  id TEXT PRIMARY KEY,
  profile_name TEXT NOT NULL,
  status TEXT NOT NULL,
  batch_size INTEGER NOT NULL,
  interval_ms INTEGER NOT NULL,
  duration_seconds INTEGER NOT NULL,
  sent_batches INTEGER NOT NULL,
  total_batches INTEGER NOT NULL,
  last_error TEXT,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ
);

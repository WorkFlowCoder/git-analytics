
-- =========================
-- INDEX (perf important)
-- =========================
CREATE INDEX IF NOT EXISTS idx_summary_repo_id ON summary(repo_id);
CREATE INDEX IF NOT EXISTS idx_contributors_repo_id ON contributors(repo_id);
CREATE INDEX IF NOT EXISTS idx_file_stats_repo_id ON file_stats(repo_id);
CREATE INDEX IF NOT EXISTS idx_activity_repo_id ON activity(repo_id);
CREATE INDEX IF NOT EXISTS idx_risk_repo_id ON risk(repo_id);
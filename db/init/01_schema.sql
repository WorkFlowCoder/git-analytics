-- =========================
-- REPOSITORIES (source de vérité)
-- =========================
CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    last_analyzed_commit TEXT,
    analyzed_at TIMESTAMP DEFAULT NOW(),
    tree JSONB
);

-- =========================
-- SUMMARY (1 repo = 1 ligne)
-- =========================
CREATE TABLE IF NOT EXISTS summary (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL UNIQUE,  -- 🔥 IMPORTANT
    commits INTEGER DEFAULT 0,
    contributors INTEGER DEFAULT 0,
    files_touched INTEGER DEFAULT 0,
    CONSTRAINT fk_summary_repo
        FOREIGN KEY (repo_id)
        REFERENCES repositories(id)
        ON DELETE CASCADE
);

-- =========================
-- CONTRIBUTORS (N lignes par repo)
-- =========================
CREATE TABLE IF NOT EXISTS contributors (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    commits INTEGER DEFAULT 0,
    is_top_contributor BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_contributors_repo
        FOREIGN KEY (repo_id)
        REFERENCES repositories(id)
        ON DELETE CASCADE
);

-- =========================
-- FILE STATS (N lignes par repo)
-- =========================
CREATE TABLE IF NOT EXISTS file_stats (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    changes INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    contributors_count INTEGER DEFAULT 0,
    churn INTEGER DEFAULT 0,
    CONSTRAINT fk_file_stats_repo
        FOREIGN KEY (repo_id)
        REFERENCES repositories(id)
        ON DELETE CASCADE
);

-- =========================
-- ACTIVITY (1 ligne / repo / jour)
-- =========================
CREATE TABLE IF NOT EXISTS activity (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    date DATE NOT NULL,
    commits INTEGER DEFAULT 0,
    CONSTRAINT unique_activity_repo_date UNIQUE (repo_id, date),  -- 🔥 IMPORTANT
    CONSTRAINT fk_activity_repo
        FOREIGN KEY (repo_id)
        REFERENCES repositories(id)
        ON DELETE CASCADE
);

-- =========================
-- RISK METRICS (1 repo = 1 ligne)
-- =========================
CREATE TABLE IF NOT EXISTS risk (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL UNIQUE,  -- 🔥 IMPORTANT
    risk_score FLOAT,
    top_contributor_share FLOAT,
    bus_factor INTEGER,
    churn_density FLOAT,
    activity_score FLOAT,
    CONSTRAINT fk_risk_repo
        FOREIGN KEY (repo_id)
        REFERENCES repositories(id)
        ON DELETE CASCADE
);
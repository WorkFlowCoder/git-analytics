import psycopg2
import json
import os

DB_DSN = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/gitanalytics"
)


def get_conn():
    return psycopg2.connect(DB_DSN)

def update_repo_tree(cur, repo_id: int, tree: dict):
    cur.execute("""
        UPDATE repositories
        SET tree = %s
        WHERE id = %s
    """, (
        json.dumps(tree),
        repo_id
    ))

# =========================
# REPOSITORY
# =========================
def get_or_create_repo(cur, name: str, path: str) -> int:
    cur.execute("""
        INSERT INTO repositories (name, path)
        VALUES (%s, %s)
        ON CONFLICT (path)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id
    """, (name, path))

    return cur.fetchone()[0]


# =========================
# SUMMARY
# =========================
def upsert_summary(cur, repo_id: int, metrics: dict, contributors: dict):
    cur.execute("""
        INSERT INTO summary (repo_id, commits, contributors, files_touched)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (repo_id)
        DO UPDATE SET
            commits = EXCLUDED.commits,
            contributors = EXCLUDED.contributors,
            files_touched = EXCLUDED.files_touched
    """, (
        repo_id,
        metrics.get("commits", 0),
        contributors.get("bus_factor", 0),
        metrics.get("files_touched", 0)
    ))


# =========================
# CONTRIBUTORS
# =========================
def insert_contributors(cur, repo_id: int, contributors_data: dict):
    for email, commits in contributors_data.get("contributors", {}).items():
        cur.execute("""
            INSERT INTO contributors (repo_id, email, commits, is_top_contributor)
            VALUES (%s, %s, %s, %s)
        """, (
            repo_id,
            email,
            commits,
            email == contributors_data.get("top_contributor")
        ))


# =========================
# FILE STATS
# =========================
def insert_file_stats(cur, repo_id: int, hotspots: list):
    for f in hotspots:
        cur.execute("""
            INSERT INTO file_stats (
                repo_id, path, changes, additions, deletions, contributors_count, churn
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            repo_id,
            f.get("file"),
            f.get("changes", 0),
            f.get("additions", 0),
            f.get("deletions", 0),
            f.get("contributors", 0),
            f.get("additions", 0) + f.get("deletions", 0)
        ))


# =========================
# ACTIVITY
# =========================
def upsert_activity(cur, repo_id: int, activity: dict):
    for date, commits in activity.get("commits_per_day", {}).items():
        cur.execute("""
            INSERT INTO activity (repo_id, date, commits)
            VALUES (%s, %s, %s)
            ON CONFLICT (repo_id, date)
            DO UPDATE SET commits = EXCLUDED.commits
        """, (
            repo_id,
            date,
            commits
        ))


# =========================
# RISK
# =========================
def upsert_risk(cur, repo_id: int, risk: dict):
    cur.execute("""
        INSERT INTO risk (
            repo_id, risk_score, top_contributor_share,
            bus_factor, churn_density, activity_score
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (repo_id)
        DO UPDATE SET
            risk_score = EXCLUDED.risk_score,
            top_contributor_share = EXCLUDED.top_contributor_share,
            bus_factor = EXCLUDED.bus_factor,
            churn_density = EXCLUDED.churn_density,
            activity_score = EXCLUDED.activity_score
    """, (
        repo_id,
        risk.get("risk_score"),
        risk.get("top_contributor_share"),
        risk.get("bus_factor"),
        risk.get("churn_density"),
        risk.get("activity_score")
    ))


# =========================
# MAIN ENTRYPOINT (FIXED)
# =========================
def persist_to_db(repo_id: int, data: dict):

    conn = get_conn()
    cur = conn.cursor()

    try:
        #print(f"[DB] repo_id = {repo_id}", flush=True)
        upsert_summary(cur, repo_id, data.get("metrics", {}), data.get("contributors", {}))
        insert_contributors(cur, repo_id, data.get("contributors", {}))
        insert_file_stats(cur, repo_id, data.get("hotspots", []))
        upsert_activity(cur, repo_id, data.get("activity", {}))
        upsert_risk(cur, repo_id, data.get("risk", {}))
        update_repo_tree(cur, repo_id, data.get("tree", {}))

        conn.commit()
        #print("[DB] commit OK", flush=True)

    except Exception as e:
        conn.rollback()
        #print("[DB ERROR]", e, flush=True)
        raise RuntimeError(f"DB persistence failed: {e}")

    finally:
        cur.close()
        conn.close()
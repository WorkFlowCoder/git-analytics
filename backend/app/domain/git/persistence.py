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
# TIMELINE
# =========================
def persist_timeline(cur, repo_id: int, timeline_data: list):
    for item in timeline_data:
        cur.execute("""
            INSERT INTO commit_timeline (
                repo_id,
                commit_hash,
                author_name,
                author_email,
                commit_date,
                commit_message,
                files_changed,
                insertions,
                deletions
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (repo_id, commit_hash)
            DO NOTHING
        """, (
            repo_id,
            item["commit_hash"],
            item["author"],
            item["email"],
            item["date"],
            item["message"],
            item["files_changed"],
            item["insertions"],
            item["deletions"]
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
        persist_timeline(cur, repo_id, data.get("timeline", []))

        conn.commit()
        #print("[DB] commit OK", flush=True)

    except Exception as e:
        conn.rollback()
        #print("[DB ERROR]", e, flush=True)
        raise RuntimeError(f"DB persistence failed: {e}")

    finally:
        cur.close()
        conn.close()

def save_graph_to_db(repo_id: int, graph):
    conn = get_conn()
    cur = conn.cursor()
    file_ids = {}
    # Clean old dependencies first
    cur.execute("""
        DELETE FROM file_dependencies
        WHERE repo_id = %s
    """, (repo_id,))
    # Insert / upsert all nodes
    for file_path in graph.nodes:
        ext = file_path.split(".")[-1]

        cur.execute("""
            INSERT INTO files (repo_id, path, language)
            VALUES (%s, %s, %s)
            ON CONFLICT (repo_id, path)
            DO UPDATE SET path = EXCLUDED.path
            RETURNING id
        """, (repo_id, file_path, ext))

        file_ids[file_path] = cur.fetchone()[0]
    # Insert edges
    for src, dst, data in graph.edges(data=True):
        src_id = file_ids.get(src)
        if not src_id:
            continue
        # if target file does not exist yet
        if dst not in file_ids:
            ext = dst.split(".")[-1]

            cur.execute("""
                INSERT INTO files (repo_id, path, language)
                VALUES (%s, %s, %s)
                ON CONFLICT (repo_id, path)
                DO UPDATE SET path = EXCLUDED.path
                RETURNING id""",
                (repo_id, dst, ext))

            file_ids[dst] = cur.fetchone()[0]

        dst_id = file_ids.get(dst)
        cur.execute(""" 
            INSERT INTO file_dependencies ( repo_id, src_file_id, dst_file_id, dep_type, raw)
            VALUES (%s, %s, %s, %s, %s)""",
            (repo_id, src_id, dst_id, data.get("type", "import"), data.get("raw")))
    conn.commit()
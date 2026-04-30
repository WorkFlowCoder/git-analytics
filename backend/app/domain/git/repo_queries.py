from app.domain.git.persistence import DB_DSN
import psycopg2

def get_conn():
    return psycopg2.connect(DB_DSN)

def get_repository(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, path, analyzed_at, tree
            FROM repositories
            WHERE id = %s
        """, (repo_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def get_summary(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT commits, contributors, files_touched
            FROM summary
            WHERE repo_id = %s
        """, (repo_id,))
        row = cur.fetchone()

        if not row:
            return None
        return {
            "commits": row[0],
            "contributors": row[1],
            "files_touched": row[2],
        }
    finally:
        cur.close()
        conn.close()

def get_contributors(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT email, commits, is_top_contributor
            FROM contributors
            WHERE repo_id = %s
            ORDER BY commits DESC
        """, (repo_id,))
        return [
            {
                "email": row[0],
                "commits": row[1],
                "is_top_contributor": row[2]
            }
            for row in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()

def get_hotspots(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT path, changes, additions, deletions, contributors_count, churn
            FROM file_stats
            WHERE repo_id = %s
            ORDER BY changes DESC
            LIMIT 50
        """, (repo_id,))
        return [
            {
                "file": row[0],
                "changes": row[1],
                "additions": row[2],
                "deletions": row[3],
                "contributors": row[4],
                "churn": row[5]
            }
            for row in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()

def get_activity(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT date, commits
            FROM activity
            WHERE repo_id = %s
            ORDER BY date ASC
        """, (repo_id,))
        return [
            {
                "date": str(row[0]),
                "commits": row[1]
            }
            for row in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()

def get_risk(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT risk_score, top_contributor_share,
                   bus_factor, churn_density, activity_score
            FROM risk
            WHERE repo_id = %s
        """, (repo_id,))
        risk_row = cur.fetchone()

        risk = None
        if risk_row:
            return {
                "risk_score": risk_row[0],
                "top_contributor_share": risk_row[1],
                "bus_factor": risk_row[2],
                "churn_density": risk_row[3],
                "activity_score": risk_row[4]
            }
    finally:
        cur.close()
        conn.close()

def get_timeline(repo_id: int, page: int = 1, limit: int = 100):
    offset = (page - 1) * limit
    conn = get_conn()
    cur = conn.cursor()
    try:
        # récupération paginée
        cur.execute("""
            SELECT
                commit_hash,
                author_name,
                author_email,
                commit_date,
                commit_message,
                files_changed,
                insertions,
                deletions
            FROM commit_timeline
            WHERE repo_id = %s
            ORDER BY commit_date DESC
            LIMIT %s
            OFFSET %s
        """, (repo_id, limit, offset))
        rows = cur.fetchall()
        for row in rows:
            print(
                "hash =", row[0],
                "| author =", row[1],
                "| date =", row[3],
                "| message =", row[4],
                flush=True
            )
        return [
            {
                #"commit_hash": row[0],
                "author_name": row[1],
                #"author_email": row[2],
                "commit_date": row[3].isoformat() if row[3] else None,
                "commit_message": row[4],
                "files_changed": row[5],
                "insertions": row[6],
                "deletions": row[7]
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()

def get_repo_graph(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Fetch nodes
        cur.execute("""SELECT id, path, language
            FROM files
            WHERE repo_id = %s
            ORDER BY path ASC
        """, (repo_id,))

        file_rows = cur.fetchall()

        nodes = []
        for row in file_rows:
            nodes.append({
                "id": row[0], "path": row[1], "language": row[2]
            })

        # Fetch edges
        cur.execute("""SELECT src_file_id, dst_file_id, dep_type, raw
            FROM file_dependencies
            WHERE repo_id = %s
        """, (repo_id,))

        dependency_rows = cur.fetchall()

        edges = []
        for row in dependency_rows:
            edges.append({
                "source": row[0],
                "target": row[1],
                "type": row[2],
                "raw": row[3]
            })

        return {
            "repo_id": repo_id,
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch dependency graph for repo_id={repo_id}: {e}"
        )

    finally:
        cur.close()
        conn.close()
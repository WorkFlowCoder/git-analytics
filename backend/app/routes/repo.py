from http.client import HTTPException
import psycopg2


from app.domain.git.persistence import DB_DSN, get_or_create_repo
from fastapi import APIRouter
from app.schemas.repo import RepoRequest
from app.services.repo_service import clone_and_analyze

from redis import Redis
from rq import Queue

from app.domain.git.clone import clone_repo
from app.jobs.git_analysis import analyze_repo_job

router = APIRouter()

def get_conn():
    return psycopg2.connect(DB_DSN)

redis_conn = Redis(host="redis", port=6379)
queue = Queue("git_jobs", connection=redis_conn)

@router.post("/repo/load")
def load_repo(request: RepoRequest):
    return clone_and_analyze(request.repo_url)

@router.get("/job/{job_id}")
def get_job(job_id: str):
    job = queue.fetch_job(job_id)

    if job is None:
        return {
            "id": job_id,
            "status": "not_found",
            "result": None
        }

    return {
        "id": job.id,
        "status": job.get_status(),
        "result": job.result
    }

@router.post("/repo/loadTest")
def load_repo(request: RepoRequest):
    repo_url = request.repo_url
    # 1. clone
    repo_path = clone_repo(repo_url)

    conn = get_conn()
    cur = conn.cursor()
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_id = get_or_create_repo(cur, repo_name, repo_path)

    conn.commit()
    cur.close()
    conn.close()
    
    # 2. enqueue job
    job = queue.enqueue(
        analyze_repo_job,
        repo_path,
        repo_url,
        repo_id
    )
    return {
        "repo": repo_url,
        "repo_id": repo_id,
        "job_id": job.id,
        "status": "queued"
    }

@router.get("/repo/{repo_id}")
def get_repo(repo_id: int):
    conn = get_conn()
    cur = conn.cursor()

    try:
        # ===== CHECK REPO =====
        cur.execute("""
            SELECT id, name, path, analyzed_at
            FROM repositories
            WHERE id = %s
        """, (repo_id,))
        repo = cur.fetchone()

        if not repo:
            raise HTTPException(status_code=404, detail="Repo not found")

        # ===== SUMMARY =====
        cur.execute("""
            SELECT commits, contributors, files_touched
            FROM summary
            WHERE repo_id = %s
        """, (repo_id,))
        summary = cur.fetchone()

        # ===== CONTRIBUTORS =====
        cur.execute("""
            SELECT email, commits, is_top_contributor
            FROM contributors
            WHERE repo_id = %s
            ORDER BY commits DESC
        """, (repo_id,))
        contributors = [
            {
                "email": row[0],
                "commits": row[1],
                "is_top_contributor": row[2]
            }
            for row in cur.fetchall()
        ]

        # ===== FILE STATS (HOTSPOTS) =====
        cur.execute("""
            SELECT path, changes, additions, deletions, contributors_count, churn
            FROM file_stats
            WHERE repo_id = %s
            ORDER BY changes DESC
            LIMIT 50
        """, (repo_id,))
        hotspots = [
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

        # ===== ACTIVITY =====
        cur.execute("""
            SELECT date, commits
            FROM activity
            WHERE repo_id = %s
            ORDER BY date ASC
        """, (repo_id,))
        activity = [
            {
                "date": str(row[0]),
                "commits": row[1]
            }
            for row in cur.fetchall()
        ]

        # ===== RISK =====
        cur.execute("""
            SELECT risk_score, top_contributor_share,
                   bus_factor, churn_density, activity_score
            FROM risk
            WHERE repo_id = %s
        """, (repo_id,))
        risk_row = cur.fetchone()

        risk = None
        if risk_row:
            risk = {
                "risk_score": risk_row[0],
                "top_contributor_share": risk_row[1],
                "bus_factor": risk_row[2],
                "churn_density": risk_row[3],
                "activity_score": risk_row[4]
            }

        return {
            "repo": {
                "id": repo[0],
                "name": repo[1],
                "url": repo[2],
                "analyzed_at": repo[3]
            },
            "summary": {
                "commits": summary[0] if summary else 0,
                "contributors": summary[1] if summary else 0,
                "files_touched": summary[2] if summary else 0
            },
            "contributors": contributors,
            "hotspots": hotspots,
            "activity": activity,
            "risk": risk
        }

    finally:
        cur.close()
        conn.close()
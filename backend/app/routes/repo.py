import psycopg2

from app.domain.git.persistence import DB_DSN, get_or_create_repo
from app.services.repo_reader import fetch_repo_details
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
    return fetch_repo_details(repo_id)
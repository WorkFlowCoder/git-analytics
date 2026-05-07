import psycopg2

from app.domain.git.persistence import DB_DSN
from app.services.repo_reader import fetch_repo_details, fetch_repo_timeline, fetch_repo_dependency_graph
from app.domain.git.repo_queries import delete_repo, prepare_repository, get_all_repos, ssh_to_https
from fastapi import APIRouter
from app.schemas.repo import RepoRequest

from redis import Redis
from rq import Queue

from app.jobs.git_analysis import analyze_repo_job

router = APIRouter()

def get_conn():
    return psycopg2.connect(DB_DSN)

redis_conn = Redis(host="redis", port=6379)
queue = Queue("git_jobs", connection=redis_conn)

@router.get("/repo")
def get_all():
    return get_all_repos()

@router.delete("/repo/{repo_id}")
def delete_repository(repo_id: int):
    delete_repo(repo_id)
    return {"status": "deleted"}

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


@router.post("/repo/load")
def load_repo(request: RepoRequest):
    repo_url = ssh_to_https(request.repo_url)
    # préparation intelligente du repo
    result = prepare_repository(repo_url)
    # Pas un lien valide
    if not result.get("repo_id"):
        return {
            "repo": repo_url,
            "status": result["status"]
        }
    # si déjà analysé et à jour → pas de job
    if not result["should_analyze"]:
        return {
            "repo": repo_url,
            "repo_id": result["repo_id"],
            "status": result["status"]
        }
    # sinon → lancer l’analyse
    job = queue.enqueue(
        analyze_repo_job,
        repo_url,
        result["repo_id"]
    )
    return {
        "repo": repo_url,
        "repo_id": result["repo_id"],
        "job_id": job.id,
        "status": "queued"
    }

@router.get("/repo/{repo_id}")
def get_repo(repo_id: int):
    return fetch_repo_details(repo_id)

@router.get("/repo/timeline/{repo_id}/{page_number}")
def get_repo_timeline(repo_id: int, page_number: int = 1):
    return fetch_repo_timeline(repo_id, page_number)

@router.get("/repo/{repo_id}/dependency-graph")
def get_repo_dependency_graph(repo_id: int):
    return fetch_repo_dependency_graph(repo_id)
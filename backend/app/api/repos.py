from redis import Redis
from rq import Queue

from app.jobs.git_analysis import analyze_repo_job

redis_conn = Redis(host="redis", port=6379)
queue = Queue("git_jobs", connection=redis_conn)

def enqueue_analysis(repo_path: str, repo_url: int, repo_id: int):

    job = queue.enqueue(
        analyze_repo_job,
        repo_path,
        repo_url,
        repo_id,
        job_timeout=3600
    )

    return {
        "job_id": job.id,
        "repo_id": repo_id,
        "status": "queued"
    }
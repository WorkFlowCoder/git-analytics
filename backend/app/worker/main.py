import os
from redis import Redis
from rq import Worker, Queue

QUEUES = ["git_jobs"]


def create_worker():
    redis_conn = Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379))
    )

    queues = [Queue(name, connection=redis_conn) for name in QUEUES]

    return Worker(queues)


if __name__ == "__main__":
    worker = create_worker()

    #print("Worker started - listening on git_jobs queue", flush=True)
    worker.work()
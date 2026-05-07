import os
from redis import Redis
from rq import Worker, Queue
from rq.registry import (
    FailedJobRegistry,
    StartedJobRegistry,
    FinishedJobRegistry
)

QUEUES = ["git_jobs"]

def clear_queues(redis_conn):
    for queue_name in QUEUES:
        queue = Queue(queue_name, connection=redis_conn)
        # Supprime les jobs en attente
        queue.empty()
        # Supprime les jobs failed
        FailedJobRegistry(queue=queue).cleanup()
        # Supprime les jobs started
        StartedJobRegistry(queue=queue).cleanup()
        # Supprime les jobs finished
        FinishedJobRegistry(queue=queue).cleanup()
        print(f"Queue cleaned: {queue_name}", flush=True)

def create_worker():
    redis_conn = Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379))
    )

    clear_queues(redis_conn)

    queues = [Queue(name, connection=redis_conn) for name in QUEUES]

    return Worker(queues)


if __name__ == "__main__":
    worker = create_worker()

    #print("Worker started - listening on git_jobs queue", flush=True)
    worker.work()
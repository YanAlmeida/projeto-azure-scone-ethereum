from src.safe_queue import get_queue
from src.smart_contract import get_contract


def get_jobs():
    jobs = get_contract().getJobs()
    for job in jobs:
        get_queue().put(job)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
import uuid
from datetime import datetime

app = FastAPI()

jobs = {}  # Armazena os detalhes dos jobs
completed_jobs = {}  # Armazena os resultados dos jobs completos
connected_machines = []  # Armazena os IDs das máquinas conectadas
jobs_by_machine = {}  # Mapeia machine_id para uma lista de job_ids
machine_index = 0  # Controla a atribuição de jobs usando round-robin

# Variáveis para o registro de processamento
is_processing_enabled = False
processed_jobs_list = []

class Job(BaseModel):
    url: HttpUrl

class JobBatch(BaseModel):
    jobs: List[HttpUrl]

class JobIDs(BaseModel):
    ids: List[str]

class JobResult(BaseModel):
    job_id: str
    char_count: int
    message: str
    processed_at: datetime = None

class ProcessingFlag(BaseModel):
    enable: bool

class JobOut(BaseModel):
    jobId: str
    url: str
    startingTimestamp: Optional[datetime] = None
    processingTimestamp: Optional[datetime] = None
    processedTimestamp: Optional[datetime] = None

class JobForMachineOut(BaseModel):
    jobId: str
    url: str

@app.post("/set-processing-flag/")
def set_processing_flag(flag: ProcessingFlag):
    global is_processing_enabled
    is_processing_enabled = flag.enable
    return {"message": f"Processing is now {'enabled' if is_processing_enabled else 'disabled'}"}

@app.get("/get-processed-jobs/")
def get_processed_jobs():
    return {"processed_jobs": processed_jobs_list}

@app.post("/submit-job/")
def submit_job(job: Job):
    global machine_index
    if not connected_machines:
        raise HTTPException(status_code=503, detail="No machines available")
    job_id = str(uuid.uuid4())
    assigned_machine = connected_machines[machine_index]
    jobs[job_id] = {'url': job.url, 'submitted_at': datetime.now(), 'assigned_machine': assigned_machine}
    
    # Atualiza jobs_by_machine
    if assigned_machine in jobs_by_machine:
        jobs_by_machine[assigned_machine].append(job_id)
    else:
        jobs_by_machine[assigned_machine] = [job_id]
    
    # Round-robin para a próxima máquina
    machine_index = (machine_index + 1) % len(connected_machines)
    return {"job_id": job_id, "assigned_to": assigned_machine}

@app.post("/submit-batch/")
def submit_batch(batch: JobBatch):
    responses = []
    for job_url in batch.jobs:
        responses.append(submit_job(Job(url=job_url)))
    return responses

@app.get("/job/{job_id}")
def get_job(job_id: str):
    if job_id in completed_jobs:
        return completed_jobs[job_id]
    elif job_id in jobs:
        return {"status": "in progress", "assigned_machine": jobs[job_id]['assigned_machine']}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.post("/connect-machine/")
def connect_machine(machine_id: str):
    if machine_id not in connected_machines:
        connected_machines.append(machine_id)
        return {"message": "Machine connected successfully", "machine_id": machine_id}
    else:
        return {"message": "Machine already connected", "machine_id": machine_id}

@app.get("/get-jobs-for-machine/{machine_id}")
def get_jobs_for_machine(machine_id: str, limit: Optional[int] = 5):
    found_jobs = []
    if machine_id in jobs_by_machine:
        for job_id in jobs_by_machine[machine_id][:limit]:
            job = jobs[job_id]
            found_jobs.append(JobForMachineOut(jobId=job_id, url=job['url']))
    
    return {"jobs": found_jobs}

@app.post("/get-jobs-by-ids/")
def get_jobs_by_ids(job_ids: JobIDs):
    found_jobs = []
    for job_id in job_ids.ids:
        if job_id in jobs:
            job = jobs[job_id]
            found_jobs.append(JobOut(
                jobId=job_id,
                url=job['url'],
                startingTimestamp=job.get('submitted_at'),
                processingTimestamp=job.get('processing_started'),
                processedTimestamp=job.get('processed_at')
            ))
    return {"jobs": found_jobs}

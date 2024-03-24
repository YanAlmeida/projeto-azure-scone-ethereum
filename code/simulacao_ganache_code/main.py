from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import time

app = FastAPI()

jobs = {}  # Armazena os detalhes dos jobs
completed_jobs = {}  # Armazena os resultados dos jobs completos
connected_machines = []  # Armazena os IDs das máquinas conectadas
jobs_by_machine = {}  # Mapeia machine_id para uma lista de job_ids
machine_index = 0  # Controla a atribuição de jobs usando round-robin
jobs_ids = 0

# Variáveis para o registro de processamento
is_processing_enabled = False
processed_jobs_list = []

class Machine(BaseModel):
    machine_id: str

class Job(BaseModel):
    fileUrl: str

class JobBatch(BaseModel):
    jobs: List[str]

class JobIDs(BaseModel):
    jobs: List[int]

class JobResult(BaseModel):
    jobId: int
    charCount: int
    message: str
    processedTimestamp: float = None

class ProcessingFlag(BaseModel):
    enable: bool

class JobOut(BaseModel):
    jobId: int
    fileUrl: str
    startingTimestamp: Optional[float] = None
    processingTimestamp: Optional[float] = None
    processedTimestamp: Optional[float] = None

class JobForMachineOut(BaseModel):
    jobId: int
    fileUrl: str


## CONECTA_MAQUINA
@app.post("/connect-machine/")
def connect_machine(machine: Machine):
    if machine.machine_id not in connected_machines:
        connected_machines.append(machine.machine_id)
        return {"message": "Machine connected successfully", "machine_id": machine.machine_id}
    else:
        return {"message": "Machine already connected", "machine_id": machine.machine_id}


## RETORNO POR MAQUINA
@app.get("/get-jobs-for-machine/{machine_id}")
def get_jobs_for_machine(machine_id: str, limit: Optional[int] = 5):
    jobs_send = []
    if machine_id in jobs_by_machine:
        jobs_send = [JobForMachineOut(jobId=job_id, fileUrl=jobs[job_id]['fileUrl']) for job_id in jobs_by_machine[machine_id][:limit]]
        jobs_by_machine[machine_id] = jobs_by_machine[machine_id][limit:]
    return {"jobs": jobs_send}


## COLETA DE DADOS
@app.post("/set-processing-flag/")
def set_processing_flag(flag: ProcessingFlag):
    global is_processing_enabled
    is_processing_enabled = flag.enable
    return {"message": f"Processing is now {'enabled' if is_processing_enabled else 'disabled'}"}

@app.get("/get-processed-jobs/")
def get_processed_jobs():
    return {"jobs": processed_jobs_list}

@app.post("/get-jobs-by-ids/")
def get_jobs_by_ids(job_ids: JobIDs):
    found_jobs = [
        JobOut(
                jobId=job_id,
                fileUrl=jobs[job_id].get('fileUrl'),
                startingTimestamp=jobs[job_id].get('startingTimestamp'),
                processingTimestamp=jobs[job_id].get('processingTimestamp'),
                processedTimestamp=jobs[job_id].get('processedTimestamp')
            )
        for job_id in job_ids.jobs if job_id in jobs
    ]

    return {"jobs": found_jobs}


## ENVIO DE JOBS
@app.post("/submit-job/")
def submit_job(job: Job):
    global machine_index
    global jobs_ids
    if not connected_machines:
        raise HTTPException(status_code=503, detail="No machines available")
    job_id = jobs_ids
    jobs_ids += 1
    assigned_machine = connected_machines[machine_index]
    jobs[job_id] = {'fileUrl': job.fileUrl, 'startingTimestamp': time.time(), 'assigned_machine': assigned_machine}
    
    # Atualiza jobs_by_machine
    if assigned_machine in jobs_by_machine:
        jobs_by_machine[assigned_machine].append(job_id)
    else:
        jobs_by_machine[assigned_machine] = [job_id]
    
    # Round-robin para a próxima máquina
    machine_index = (machine_index + 1) % len(connected_machines)
    return {"jobId": job_id}

@app.post("/submit-batch/")
def submit_batch(batch: JobBatch):
    responses = [submit_job(Job(fileUrl=job_url)) for job_url in batch.jobs]
    return responses


## RESULTADOS
@app.post("/submit-result/")
def submit_result(results: List[JobResult]):
    time_r = time.time()
    [set_result(result, time_r) for result in results]
    return

def set_result(result: JobResult, time_r):
    if is_processing_enabled:
        processed_jobs_list.append(result.jobId)
    result.processedTimestamp = time_r
    jobs[result.jobId]['processedTimestamp'] = result.processedTimestamp
    jobs[result.jobId]['charCount'] = result.charCount

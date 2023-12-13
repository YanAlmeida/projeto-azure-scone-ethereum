from src.smart_contract import get_contract, Job
from typing import Dict, List
import requests
import os
import socket
import json
import PyPDF2
import io
import asyncio
import aiohttp
import newrelic.agent


TEE_ADDRESS = os.environ.get("TEE_ADDRESS")
CONNECTION_TUPLE = tuple(TEE_ADDRESS.split(":"))


@newrelic.agent.function_trace()
def send_data_to_tee(message):
    """
    Função para envio dos dados ao TEE e dos resultados à blockchain
    :return:
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((CONNECTION_TUPLE[0], int(CONNECTION_TUPLE[1])))
        final_string = json.dumps(message) + "#END_OF_TRANSMISSION#"
        sock.sendall(final_string.encode("utf-8"))
        received = sock.recv(64*1024).decode("utf-8") #64 KB

    return received


async def fetch_job_text(session: 'Session', job: Job) -> Dict[str, str]:
    """
    Função para fetch de texto referenciado pela URL do job
    :param session: Sessão do aiohttp
    :param job: Job cujos dados serão buscados
    :return: Job completo, com status e message preenchidos
    """
    try:
        async with session.get(job['fileUrl']) as response:
            response.raise_for_status() 
            response.encoding = 'utf-8'
            content = await response.read()
            total_response = ""
            file = io.BytesIO(content)
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                total_response += page.extract_text()
            job["message"] = total_response
            job["status"] = "FETCHED"
    except Exception as e:
        job["status"] = "ERROR"
        job["message"] = None
    return job


@newrelic.agent.function_trace()
async def fetch_jobs(jobs: List[Job]):
    """
    Função para fetch de lista de jobs
    :param jobs: lista de jobs
    :return: lista de jobs completos
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_job_text(session, job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


@newrelic.agent.function_trace()
def get_and_process_jobs():
    """
    Thread para recuperação dos Jobs no contrato, busca dos dados referenciados
    por ele e envio à fila
    :return:
    """
    jobs = get_contract().getJobsMachine()
    fetched_data = asyncio.run(fetch_jobs(jobs))
    to_process = []
    for job in fetched_data:
        if job["status"] == "ERROR":
            get_contract().submitResults([
                {"jobId": job["jobId"],
                 "charCount": 0,
                 "message": "ERROR:FILE_CANT_BE_FETCHED"}
            ])
            newrelic.agent.record_exception()
            continue
        to_process.append(job)
    final_data = send_data_to_tee(to_process)
    get_contract().submitResults(json.loads(final_data))

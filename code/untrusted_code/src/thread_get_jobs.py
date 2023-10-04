from src.safe_queue import get_queue
from src.smart_contract import get_contract
from src.smart_contract import Job
import requests


def fetch_job_text(url: str) -> str:
    """
    Função para fetch de texto referenciado pela URL do job
    :param url: url de onde buscar o arquivo texto
    :return: texto retornado pela URL
    """
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.text


def get_jobs():
    """
    Thread para recuperação dos Jobs no contrato, busca dos dados referenciados
    por ele e envio à fila
    :return:
    """
    jobs = get_contract().getJobs()
    for job in jobs:
        try:
            job_data = fetch_job_text(job["fileUrl"])
            get_queue().put({**job, **{"message": job_data}})
        except requests.HTPPError:
            get_contract().submitResults([
                {"jobId": job["jobId"],
                 "charCount": 0,
                 "message": "ERROR:FILE_CANT_BE_FETCHED"}
            ])

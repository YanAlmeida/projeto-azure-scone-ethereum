from src.smart_contract import get_contract
import requests
import os
import socket
import json


TEE_ADDRESS = os.environ.get("TEE_ADDRESS")


def process_data(message):
    """
    Função para envio dos dados ao TEE e dos resultados à blockchain
    :return:
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(tuple(TEE_ADDRESS.split(":")))
        sock.sendall(json.dumps(message).encode("utf-8"))
        received = sock.recv(1024).decode("utf-8")
        get_contract().submitResults([json.loads(received)])
    return


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
            process_data({**job, **{"message": job_data}})
        except requests.HTPPError:
            get_contract().submitResults([
                {"jobId": job["jobId"],
                 "charCount": 0,
                 "message": "ERROR:FILE_CANT_BE_FETCHED"}
            ])

import os
from typing import Tuple, List, Dict, Union, Any
import requests

Job = Dict[str, Union[int, str]]
Result = Dict[str, Union[int, str]]


class SmartContract:
    url = os.environ.get("BLOCKCHAIN_ADDRESS", "http://18.223.172.239:8545")

    def setResultValue(self, value: bool):
        response = requests.post(f"{self.url}/set-processing-flag/", json={"enable": value})
        response.raise_for_status()
        return response.status_code

    def submitJobBatch(self, urls: List[str]):
        """
        Método para submissão de novos jobs
        :param url: URL contendo arquivo com os dados do job
        :return: Inteiro representando o ID do job criado no contrato
        inteligente
        """
        
        response = requests.post(f"{self.url}/submit-batch/", json={"jobs": urls})
        response.raise_for_status()
        return
    
    def returnJobsIds(self):
        response = requests.get(f"{self.url}/get-processed-jobs/")
        response.raise_for_status()
        return response.json()['jobs']

    def getJobs(self, jobs_ids):
        response = requests.post(f"{self.url}/get-jobs-by-ids/", json={'jobs': jobs_ids})
        response.raise_for_status()
        return response.json()['jobs']

CONTRACT = {}


def get_contract(account_number) -> SmartContract:
    """
    Função para retorno de objeto para interação com o contrato inteligente.
    :return: Instância de 'SmartContract' (única na aplicação)
    """
    global CONTRACT
    if CONTRACT.get(account_number) is None:
        CONTRACT[account_number] = SmartContract()
    return CONTRACT[account_number]


def erase_cache():
    global CONTRACT
    CONTRACT = {}

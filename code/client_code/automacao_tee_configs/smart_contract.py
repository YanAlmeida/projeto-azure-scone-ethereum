import os
from typing import Tuple, List, Dict, Union, Any
import requests

Job = Dict[str, Union[int, str]]
Result = Dict[str, Union[int, str]]


class SmartContract:
    url = os.environ.get("BLOCKCHAIN_ADDRESS", "http://18.223.172.239:8545")

    def setResultValue(self, value: bool) -> int:
        response = requests.post(f"{self.url}/set-processing-flag/", json={"enable": value})
        response.raise_for_status()
        return response.status_code

    def submitJobBatch(self, urls: List[str]) -> int:
        """
        Método para submissão de novos jobs
        :param url: URL contendo arquivo com os dados do job
        :return: Inteiro representando o ID do job criado no contrato
        inteligente
        """
        
        response = requests.post(f"{self.url}/submit-batch/", json={"jobs": urls})
        response.raise_for_status()
        return
    
    def returnJobsIds(self) -> int:
        response = requests.get(f"{self.url}/get-processed-jobs/")
        response.raise_for_status()
        return response.json()['processed_jobs']

    def getJobs(self, jobs_ids=[]) -> int:
        response = requests.post(f"{self.url}/get-jobs-by-ids/", json={'ids': jobs_ids})
        response.raise_for_status()
        return response.json()['jobs']


MNEMONIC_WORDS = os.environ.get("MNEMONIC",
                                "nation quality celery volume loan west master little expand card hire shell")
DERIVATION_PATH = os.environ.get("DERIVATION_PATH", "m/44'/60'/0'/0")
CONTRACT_ABI = os.environ.get("CONTRACT_ABI",
                              '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"},{"indexed":false,"internalType":"uint256","name":"_value","type":"uint256"}],"name":"ReturnUInt","type":"event"},{"inputs":[],"name":"collectResults","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"connectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"connectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disconnectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"disconnectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"idList","type":"uint256[]"}],"name":"getJobs","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"},{"internalType":"uint256[]","name":"startingTimes","type":"uint256[]"},{"internalType":"uint256[]","name":"processingTimes","type":"uint256[]"},{"internalType":"uint256[]","name":"endingTimes","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"}],"name":"getJobsMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getJobsMachineView","outputs":[{"internalType":"uint256[]","name":"jobsIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"name":"getResult","outputs":[{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"heartBeat","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobProcessingInfo","outputs":[{"internalType":"uint256","name":"waitingTimestamp","type":"uint256"},{"internalType":"uint256","name":"processingTimestamp","type":"uint256"},{"internalType":"uint256","name":"currentStatus","type":"uint256"},{"internalType":"address","name":"responsibleMachine","type":"address"},{"internalType":"uint256","name":"indexInJobs","type":"uint256"},{"internalType":"uint256","name":"indexInMachine","type":"uint256"},{"internalType":"uint256","name":"processedTimestamp","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobProcessingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobUpdateInterval","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobWaitingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"string","name":"fileUrl","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastJobId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"processedJobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"resetProcessedJobs","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"resultsPerJobId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"returnJobsIds","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bool","name":"value","type":"bool"}],"name":"setResultValue","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"url","type":"string"}],"name":"submitJob","outputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string[]","name":"urls","type":"string[]"}],"name":"submitJobBatch","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"},{"internalType":"uint256[]","name":"_charCounts","type":"uint256[]"},{"internalType":"string[]","name":"_messages","type":"string[]"}],"name":"submitResults","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS",
                                  '0x5b92A0289CBeBacC143842122bC3c5B78e5584FB')


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

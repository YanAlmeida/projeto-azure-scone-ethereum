import threading
import time
from typing import List

from src.smart_contract import get_contract, check_contract_available
from src.thread_get_jobs import get_jobs
from src.thread_heart_beat import heart_beat

POLL_INTERVAL = 10  # seconds

import os

os.environ["MNEMONIC"] = "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
os.environ["DERIVATION_PATH"] = "m/44'/60'/0'/0"
os.environ["BLOCKCHAIN_ADDRESS"] = "http://20.65.93.178:8545"
os.environ["CONTRACT_ABI"] = """[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"}],"name":"NotifyMachines","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"_jobId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"_charCount","type":"uint256"},{"indexed":false,"internalType":"string","name":"_message","type":"string"}],"name":"NotifyResult","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"},{"indexed":false,"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"},{"indexed":false,"internalType":"string[]","name":"_filesUrls","type":"string[]"}],"name":"ReturnJobs","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"},{"indexed":false,"internalType":"uint256","name":"_value","type":"uint256"}],"name":"ReturnUInt","type":"event"},{"inputs":[],"name":"connectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"connectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disconnectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"disconnectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getJobs","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getJobsMachine","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"name":"getResult","outputs":[{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"heartBeat","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobProcessingInfo","outputs":[{"internalType":"uint256","name":"waitingTimestamp","type":"uint256"},{"internalType":"uint256","name":"processingTimestamp","type":"uint256"},{"internalType":"uint256","name":"processedTimestamp","type":"uint256"},{"internalType":"string","name":"currentStatus","type":"string"},{"internalType":"address","name":"responsibleMachine","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobProcessingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobUpdateInterval","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobWaitingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPROCESSEDPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPROCESSINGPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"string","name":"fileUrl","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsProcessed","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsProcessing","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsWAITINGPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsWaiting","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"resultsPerJobId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"url","type":"string"}],"name":"submitJob","outputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"},{"internalType":"uint256[]","name":"_charCounts","type":"uint256[]"},{"internalType":"string[]","name":"_messages","type":"string[]"}],"name":"submitResults","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
os.environ["CONTRACT_ADDRESS"] = "0x8CdaF0CD259887258Bc13a92C0a6dA92698644C0"

def get_blockchain_notifications() -> List:
    """
    Função para monitoramento de eventos de alocação de jobs para a máquina no
    contrato inteligente
    :return: Lista de logs referentes a jobs alocados para a máquina
    """
    return get_contract().get_job_notification_filter().get_new_entries()


if __name__ == '__main__':
    while not check_contract_available():
        time.sleep(POLL_INTERVAL)
        continue
    try:
        get_contract().connectMachine()
    except:
        get_contract().disconnectMachine()
        get_contract().connectMachine()

    thread_heart_beat = threading.Thread(target=heart_beat)
    thread_heart_beat.start()

    while True:
        if len(get_blockchain_notifications()) > 0:
            thread_get_jobs = threading.Thread(target=get_jobs)
            thread_get_jobs.start()
        time.sleep(POLL_INTERVAL)

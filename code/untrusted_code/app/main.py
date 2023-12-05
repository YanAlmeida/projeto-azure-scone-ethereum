import threading
import time
from typing import List

from src.smart_contract import get_contract, check_contract_available
from src.thread_get_jobs import get_jobs
from src.thread_heart_beat import heart_beat

POLL_INTERVAL = 10  # seconds


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
    get_contract().connectMachine()

    thread_heart_beat = threading.Thread(target=heart_beat)
    thread_heart_beat.start()

    while True:
        if len(get_blockchain_notifications()) > 0:
            thread_get_jobs = threading.Thread(target=get_jobs)
            thread_get_jobs.start()
        time.sleep(POLL_INTERVAL)

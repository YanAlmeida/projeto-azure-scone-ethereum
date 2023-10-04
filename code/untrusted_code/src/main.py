import threading
import time
from typing import List

from smart_contract import get_contract
from src.thread_get_jobs import get_jobs
from src.thread_heart_beat import heart_beat
from src.thread_send_results_blockchain import send_results_blockchain
from src.thread_write_pipe import write_pipe

POLL_INTERVAL = 10  # seconds


def get_blockchain_notifications() -> List:
    """
    Função para monitoramento de eventos de alocação de jobs para a máquina no
    contrato inteligente
    :return: Lista de logs referentes a jobs alocados para a máquina
    """
    return get_contract().get_job_notification_filter().get_new_entries()


if __name__ == '__main__':
    get_contract().connectMachine()
    thread_write_pipe = threading.Thread(target=write_pipe)
    thread_write_pipe.start()

    thread_heart_beat = threading.Thread(target=heart_beat)
    thread_heart_beat.start()

    thread_send_results_blockchain = threading.Thread(
        target=send_results_blockchain
    )
    thread_send_results_blockchain.start()

    while True:
        if len(get_blockchain_notifications()) > 0:
            thread_get_jobs = threading.Thread(target=get_jobs)
        time.sleep(POLL_INTERVAL)

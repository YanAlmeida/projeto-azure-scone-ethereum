import threading
import time
from typing import List

from src.smart_contract import get_contract, check_contract_available
from src.thread_get_jobs import get_and_process_jobs
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
    # Verifica a disponibilidade do contrato inteligente
    while not check_contract_available():
        time.sleep(POLL_INTERVAL)
        continue
    # Efetua a conexão ao contrato inteligente
    try:
        get_contract().connectMachine()
    except:
        get_contract().disconnectMachine()
        get_contract().connectMachine()

    # Inicia a thread heart_beat
    thread_heart_beat = threading.Thread(target=heart_beat)
    thread_heart_beat.start()

    # Monitora constantemente os eventos da blockchain , aguardando notificacoes de jobs alocados para ela
    while True:
        if len(get_blockchain_notifications()) > 0:
            thread_get_jobs = threading.Thread(target=get_and_process_jobs)
            thread_get_jobs.start()
        time.sleep(POLL_INTERVAL)

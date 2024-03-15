import threading
import time
from typing import List

from src.smart_contract import get_contract, check_contract_available
from src.thread_get_jobs import get_and_process_jobs
from src.thread_heart_beat import heart_beat
from concurrent.futures import ThreadPoolExecutor
import os

POLL_INTERVAL = 10  # seconds


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

    with ThreadPoolExecutor(max_workers=20) as executor:

        # Inicia a thread heart_beat
        executor.submit(heart_beat)

        # Monitora constantemente os eventos da blockchain , aguardando notificacoes de jobs alocados para ela
        while True:
            jobs = get_contract().pollJobs()
            if len(jobs) > 0:
                executor.submit(get_and_process_jobs(jobs))
            time.sleep(POLL_INTERVAL)

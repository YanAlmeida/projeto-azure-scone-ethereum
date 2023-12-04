from typing import Callable

from src.safe_queue import get_queue
from src.user_types import Job


def generate_count_chars(message: Job) -> Callable:
    """
    Função para retorno de função representando
    thread que processa e insere dados na fila
    :param message: Job a ser processado
    :return: Função representando a thread
    """

    def count_chars():
        try:
            get_queue().put({"jobId": message["jobId"],
                             "charCount": len(
                                 message["message"]),
                             "message": "SUCESSO"})
        except:
            get_queue().put({"jobId": message["jobId"],
                             "charCount": 0,
                             "message": "FALHA"})

    return count_chars

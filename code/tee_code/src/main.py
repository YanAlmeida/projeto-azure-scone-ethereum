import json
import threading
import os

from src.thread_count_chars import generate_count_chars
from src.thread_write_pipe import write_pipe

READ_PIPE_PATH = os.environ.get("READ_PIPE_PATH")


def read_pipe():
    """
    Função para execução na thread principal para recebimento de dados a
    processar por parte do código externo
    :return:
    """
    if not os.path.exists(READ_PIPE_PATH):
        os.mkfifo(READ_PIPE_PATH)
    with open(READ_PIPE_PATH, 'r') as pipe:
        while True:
            message = json.loads(pipe.readline())
            if message:
                thread_count_chars = threading.Thread(
                    target=generate_count_chars(message)
                )
                thread_count_chars.start()
            else:  # Indica que a pipe foi fechada
                break


if __name__ == "__main__":
    thread_write_pipe = threading.Thread(target=write_pipe)
    thread_write_pipe.start()
    while True:
        read_pipe()

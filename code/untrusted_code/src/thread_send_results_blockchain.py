import json
import os

from src.smart_contract import get_contract

READ_PIPE_PATH = os.environ.get("READ_PIPE_PATH")


def send_results_blockchain():
    if not os.path.exists(READ_PIPE_PATH):
        os.mkfifo(READ_PIPE_PATH)
    with open(READ_PIPE_PATH, "r") as pipe:
        while True:
            result = json.loads(pipe.readline())
            get_contract().submitResults([result])

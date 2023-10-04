import json
import os

from src.safe_queue import get_queue

WRITE_PIPE_PATH = os.environ.get("WRITE_PIPE_PATH")


def write_pipe():
    if not os.path.exists(WRITE_PIPE_PATH):
        os.mkfifo(WRITE_PIPE_PATH)
    with open(WRITE_PIPE_PATH, "w") as pipe:
        while True:
            data = json.dumps(get_queue().get())
            pipe.write(data + "\n")
            pipe.flush()

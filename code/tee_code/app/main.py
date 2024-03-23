import socket
from src.thread_accept_connection import accept_connection, read_file_connection
from concurrent.futures import ThreadPoolExecutor
import os


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=6) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("0.0.0.0", 9090))
            server.listen()
            while True:
                connection, client_address = server.accept()
                executor.submit(read_file_connection(connection, executor))

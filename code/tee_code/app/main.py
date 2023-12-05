import threading
import socket
from src.thread_accept_connection import accept_connection


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("0.0.0.0", 9090))
        server.listen()
        while True:
            connection, client_address = server.accept()
            process_thread = threading.Thread(target=accept_connection(connection))
            process_thread.start()

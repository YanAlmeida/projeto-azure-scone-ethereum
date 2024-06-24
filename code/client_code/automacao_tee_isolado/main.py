from locust import User, task, constant, events
import pytz
import time
from datetime import datetime
import os
import socket
import traceback

WAIT_TIME = float(os.environ.get("WAIT_TIME"))
TEE_ADDRESS = os.environ.get("TEE_ADDRESS")


def log_response_time(request_type, name, response_time, **kwargs):
    # Here we write the response time to a text file
    with open('/tmp/response_times.txt', 'a') as file:
        file.write(f"{response_time}\n")

events.request.add_listener(log_response_time)

def timestamp_to_string(timestamp):
    datetime_value = datetime.fromtimestamp(timestamp, tz=pytz.timezone('America/Sao_Paulo'))
    return datetime_value.strftime("%Y-%m-%d %H:%M:%S")


class TEEUser(User):
    wait_time = constant(0)  # Define wait time between tasks
    _file = None

    def on_start(self):
        host, rps = self.host.split('/')
        print(f"INICIANDO TESTE PARA {host} a {rps}")
        host_size = host.split('_')[1].split('.')[0]
        if TEEUser._file is None:
            file = open(host, 'rb')
            TEEUser._file = file.read()
            file.close()
            with open(f'/tmp/DADOS_TESTES.txt', 'a') as f:
                f.write(f'START {host_size}-{rps}: {timestamp_to_string(time.time())}\n')
        self._file = TEEUser._file

    def on_stop(self):
        host, rps = self.host.split('/')
        host_size = host.split('_')[1].split('.')[0]
        if TEEUser._file is not None:
            TEEUser._file = None
            with open(f'/tmp/DADOS_TESTES.txt', 'a') as f:
                f.write(f'END {host_size}-{rps}: {timestamp_to_string(time.time())}\n#\n')
        self._file = None

    @task
    def send_request_to_tee(self):
        
        try:
            inicio = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((TEE_ADDRESS, 9090))
                header = "BEGIN#10##"
                footer = "#END_OF_TRANSMISSION#"

                full_buffer = bytes(header, 'utf-8') + self._file + bytes(footer, 'utf-8')
                client_socket.sendall(full_buffer)
                client_socket.recv(1024)
            meio = time.time()

            events.request.fire(
                **{
                        "request_type": "tee_interaction",
                        "name": "send_request_to_tee",
                        "response_time": (meio - inicio) * 1000,
                        "response_length": 0
                    }
            )

            fim = time.time()

            tempo = fim - inicio

            if tempo > WAIT_TIME:
                tempo = WAIT_TIME

            time.sleep(WAIT_TIME - tempo)
        except Exception as e:
            exc = traceback.format_exc()
            print(exc)

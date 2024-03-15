from locust import User, task, constant, events
import pytz
from utils import read_pdf, send_data_to_tee
import time
from smart_contract import get_contract
from datetime import datetime


def append_times_file(mode, test_identificator):
    filename = "D:\\backup_yan\\Desktop\\TCC\\RELATORIOS\\DADOS - TESTES\\DADOS_TESTES.txt"
    sao_paulo_timezone = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz=sao_paulo_timezone).strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, 'a') as file:
        file.write(f"{mode} {test_identificator}: {now}\n")
        if mode == 'END':
            file.write("#\n")


class TEEUser(User):
    wait_time = constant(1)  # Define wait time between tasks
    _user_id = 3
    _contract = None

    def on_start(self):
        identifier = self.host.split('/')[-1].split('?')
        self._identifier = identifier[0].strip('output_').strip('.pdf') + '-' + identifier[1]
        append_times_file('START', self._identifier)
        self._contract = get_contract(self._user_id)
        TEEUser._user_id += 1

    def on_stop(self):
        append_times_file('END', self._identifier)

    @task
    def send_request_to_tee(self):
        inicio = time.time()
        self._contract.submitJob(self.host, synchronous=False)
        fim = time.time()

        events.request.fire(
            **{
                    "request_type": "tee_interaction",
                    "name": "send_request_to_tee",
                    "response_time": (fim - inicio) * 1000,
                    "response_length": 0
                }
        )

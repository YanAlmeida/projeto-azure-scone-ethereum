from locust import User, task, constant, events
import pytz
import time
from smart_contract import get_contract, erase_cache
from datetime import datetime
import os

BATCH_SIZE = 25
WAIT_TIME = 10


class TEEUser(User):
    wait_time = constant(0)  # Define wait time between tasks
    _user_count = list(range(3, 999))
    _contract = None
    value = None

    def on_start(self):
        value = TEEUser._user_count.pop()
        self.value = value
        TEEUser._user_count = [value] + TEEUser._user_count
        self._contract = get_contract(value)
        if self.value == 998:
            print(self._contract._execute_transaction_method('setResultValue', True))

    def on_stop(self):
        if self.value == 998:
            print(self._contract._execute_transaction_method('setResultValue', False, gas_price='150'))
        erase_cache()
        self._contract = None

    @task
    def send_request_to_tee(self):
        inicio = time.time()
        self._contract.submitJobBatch([self.host]*BATCH_SIZE, synchronous=False)
        meio = time.time()

        for _ in range(BATCH_SIZE):
            events.request.fire(
                **{
                        "request_type": "tee_interaction",
                        "name": "send_request_to_tee",
                        "response_time": (meio - inicio) * 1000,
                        "response_length": 0
                    }
            )
        fim = time.time()
        tempo = WAIT_TIME - (fim - inicio)
        if (tempo) < 0:
            tempo = 0
        time.sleep(tempo)

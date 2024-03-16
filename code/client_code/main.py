from locust import User, task, constant, events
import pytz
import time
from smart_contract import get_contract, erase_cache
from datetime import datetime


class TEEUser(User):
    wait_time = constant(0)  # Define wait time between tasks
    _user_count = list(range(3, 999))
    _contract = None

    def on_start(self):
        value = TEEUser._user_count.pop()
        TEEUser._user_count = [value] + TEEUser._user_count
        self._contract = get_contract(value)

    def on_stop(self):
        erase_cache()
        self._contract = None

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

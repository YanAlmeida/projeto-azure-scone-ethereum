from queue import Empty
from src.smart_contract import get_contract
from src.event_thread import event_thread
from locust import User, task, events
import multiprocessing
from src.async_task import async_thread, MAX_JOBS_RUN, SIZE, TEE
import multiprocessing
import threading
from itertools import cycle
import copy
import pytz


def gerar_arquivos_txt(tamanho, rps, tee):
    from datetime import datetime

    sao_paulo_timezone = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz=sao_paulo_timezone).strftime("%d_%m_%Y__%H_%M")
    open(f"D:\\backup_yan\\Desktop\\TCC\\RELATORIOS\\Dados - {tee} TEE\\{tamanho}\\{now}__{rps}RPS__TEE.txt", 'a').close()
    open(f"D:\\backup_yan\\Desktop\\TCC\\RELATORIOS\\Dados - {tee} TEE\\{tamanho}\\{now}__{rps}RPS__E2E.txt", 'a').close()
    return

class SmartContractUser(User):
    wait_time = lambda _: 60/MAX_JOBS_RUN  # Define wait time between tasks
    _initial_counter = 3
    _user_count = cycle(range(_initial_counter, 199))
    _process = None
    _thread = None

    _queue_to_process = None
    _queue_to_user = multiprocessing.Manager().Queue()
    user_id = None
    first_id = None

    def on_start(self):
        gerar_arquivos_txt(SIZE, int(MAX_JOBS_RUN/60), TEE)
        # Increment the user count for each new user
        self.user_id = next(SmartContractUser._user_count)
        self._user_count = copy.deepcopy(SmartContractUser._user_count)

        # Starts id list
        if SmartContractUser.first_id is None:
            SmartContractUser.first_id = get_contract(self.user_id).submitJob('https://drive.usercontent.google.com/uc?id=1C21zZm42v5BOC9oiXHPtODnoYFBDl2-8&export=download')
            print(SmartContractUser.first_id)
        self.first_id = SmartContractUser.first_id + (MAX_JOBS_RUN * (self.user_id - self._initial_counter))
        print(self.first_id)
        # Starts async calls process
        if self._process is None:
            self._queue_to_process = multiprocessing.Queue()
            self._process = multiprocessing.Process(target=async_thread, args=(self._queue_to_process, SmartContractUser._queue_to_user, self.first_id))
            self._process.start()

        # Starts firing events thread
        if SmartContractUser._thread is None:
            SmartContractUser._thread = threading.Thread(target=event_thread, args=(SmartContractUser._queue_to_user, self.fire_event))
            SmartContractUser._thread.start()

    def on_stop(self):
        # Stop the background thread when the last user stops
        if self._process is not None:
            self._process.terminate()
            self._process.join()
            self._process = None

        if self.user_id == self._initial_counter + 1 and SmartContractUser._thread is not None:
            SmartContractUser._queue_to_user.put(None)
            SmartContractUser._thread.join()
            SmartContractUser._thread = None

    def fire_event(self, **kwargs):
        events.request.fire(**kwargs)

    @task
    def add_request(self):
        self._queue_to_process.put(next(self._user_count))
        return

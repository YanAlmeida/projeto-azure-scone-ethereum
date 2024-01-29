from queue import Empty
from src.smart_contract import get_contract
from src.event_thread import event_thread
from locust import User, task, events
import multiprocessing
from src.async_task import async_thread
import multiprocessing
import threading


class SmartContractUser(User):
    wait_time = lambda _: 1  # Define wait time between tasks
    _user_count = 0
    _process = None
    _thread = None

    _queue_to_process = multiprocessing.Queue()
    _queue_to_user = multiprocessing.Manager().Queue()
    user_id = 0
    first_id = None

    def on_start(self):

        # Increment the user count for each new user
        SmartContractUser._user_count += 1
        self.user_id = SmartContractUser._user_count

        # Starts id list
        if self.first_id is None:
            self.first_id = get_contract(self.user_id).submitJob('https://drive.usercontent.google.com/uc?id=1C21zZm42v5BOC9oiXHPtODnoYFBDl2-8&export=download')

        # Starts async calls process
        if SmartContractUser._process is None:
            SmartContractUser._process = multiprocessing.Process(target=async_thread, args=(SmartContractUser._queue_to_process, SmartContractUser._queue_to_user, self.first_id))
            SmartContractUser._process.start()

        # Starts firing events thread
        if SmartContractUser._thread is None:
            SmartContractUser._thread = threading.Thread(target=event_thread, args=(SmartContractUser._queue_to_user, self.fire_event))
            SmartContractUser._thread.start()

    def on_stop(self):
        # Stop the background thread when the last user stops
        if self.user_id == 1 and SmartContractUser._process is not None:
            SmartContractUser._process.terminate()
            SmartContractUser._process.join()
            SmartContractUser._process = None

            SmartContractUser._queue_to_user.put(None)
            SmartContractUser._thread.join()
            SmartContractUser._thread = None

    def fire_event(self, **kwargs):
        events.request.fire(**kwargs)

    @task
    def add_request(self):
        self._queue_to_process.put(self.user_id)
        return

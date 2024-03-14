import uuid
from src.smart_contract import get_contract
import time
import asyncio

MAX_JOBS_RUN = 180
SIZE = '7mb'
TEE = 3

JOBS_SENT = 0
DICT_STARTING_TIMES = {}
LINKS = {
    '300kb': 'https://drive.usercontent.google.com/u/2/uc?id=1i44QAfEqRPDZD8v3_BJmVeirU6U70WBu&export=download',
    '400kb': 'https://drive.usercontent.google.com/u/2/uc?id=1b0YDX_5h6bv7HLiG1YOCISOs6G4Y-MQQ&export=download',
    '500kb': 'https://drive.usercontent.google.com/u/2/uc?id=1fZCNpRAOW_nrpsCNACOg0Goa67fK2LX5&export=download',
    '600kb': 'https://drive.usercontent.google.com/u/2/uc?id=14ygGddj3og1MmUKHWQSMMO1EUe1UBqUB&export=download',
    '700kb': 'https://drive.usercontent.google.com/u/2/uc?id=1sutMjDSAXuRuYoezHz1fzNq5Lw9ZhNq4&export=download',
    '800kb': 'https://drive.usercontent.google.com/u/2/uc?id=1sBtErWIZioLBC2QN_cz4Y1f_tNn0DoVz&export=download',
    '900kb': 'https://drive.usercontent.google.com/u/2/uc?id=1-EYAsqQ5b7eutPEl_6GMA1llTK2GtKp3&export=download',
    '1mb': 'https://drive.usercontent.google.com/u/2/uc?id=1vmmaIoVdikq8rRAuzKDjm7b53iwqSyyS&export=download',
    '2mb': 'https://drive.usercontent.google.com/u/2/uc?id=1DS1faZwa9WTgMH2Sw1D4OiAhLCiJtxU7&export=download',
    '3mb': 'https://drive.usercontent.google.com/u/2/uc?id=1yuI2eBKbtp8ILGJuWrAFSM3GRUlaBt8v&export=download',
    '4mb': 'https://drive.usercontent.google.com/u/2/uc?id=1ZnXQzQFg0Ei0Gxq74uTCfvcLzEbcQgcw&export=download',
    '5mb': 'https://drive.usercontent.google.com/u/2/uc?id=1b7tXdUE74yDNd-kYGRLKfz68vCc6dRIf&export=download',
    '6mb': 'https://drive.usercontent.google.com/u/2/uc?id=1UiY-nGe9Yvl8fhmMXZ6M1YWd5tTJ5sWb&export=download',
    '7mb': 'https://drive.usercontent.google.com/u/2/uc?id=1W81_T39zBglF63S4KFdSnmLGJ8Us1N7O&export=download',
    '8mb': 'https://drive.usercontent.google.com/u/2/uc?id=1ShkZ5I0t08CCNDItwBjOTu2wBvQLD0Iv&export=download',
    '9mb': 'https://drive.usercontent.google.com/u/2/uc?id=1lS8omlZx3jMj16QOLBi4RUo-ZXuPbWEi&export=download',
    '10mb': 'https://drive.usercontent.google.com/u/2/uc?id=1qOVHrBdJOw__TLS22ZlmghxHT-x7xHQl&export=download'
}


def async_thread(queue_requests, queue_eventos, initial_value):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(poller_loop(queue_requests, queue_eventos, initial_value))


async def poller_loop(queue_requests, queue_eventos, initial_value):
    global JOBS_PACK_SENT
    global JOBS_SENT
    start_time = time.time()
    tasks = []
    try:
        while True:
            if JOBS_SENT < MAX_JOBS_RUN:
                if not queue_requests.empty():
                    initial_value += 1
                    tasks.append(asyncio.create_task(submit_job_and_get_result(queue_requests.get(), initial_value)))
                    JOBS_SENT += 1
            else:
                break
            await asyncio.sleep(0.1)
    finally:
        await asyncio.gather(*tasks)
        print(f"ENVIO DE {JOBS_SENT} JOBS FINALIZADO EM: {time.time() - start_time}s")
        queue_eventos.put(DICT_STARTING_TIMES)

async def submit_job_and_get_result(user_count, job_id):
    contract = await asyncio.get_running_loop().run_in_executor(None, get_contract, user_count)  # Get the smart contract instance

    # Start measuring time
    start_time = time.time()

    # Submit a job
    try:
        await asyncio.get_running_loop().run_in_executor(None, contract.submitJob, LINKS[SIZE], False)
        DICT_STARTING_TIMES[job_id] = start_time
    except:
        del DICT_STARTING_TIMES[job_id]
        print(job_id)

    return

# async def submit_job_and_get_result(user_count, queue_eventos):
#     # contract = get_contract(user_count)  # Get the smart contract instance

#     # Start measuring time
#     start_time = time.time()
#     timeout = 600  # Set a timeout (in seconds)

#     await asyncio.sleep(2)

#     # Submit a job
#     job_id = uuid.uuid4()
#     print(job_id)
#     # Wait for the result with timeout
#     while True:
#         await asyncio.sleep(1)
#         result = {"message": "SUCESSO", "charCount": 10}
#         if result['message']:
#             end_time = time.time()
#             total_time = end_time - start_time
#             if result['message'] != 'SUCESSO':
#                 queue_eventos.put(
#                     {
#                         "request_type": "smart_contract_interaction",
#                         "name": "submit_job_and_get_result",
#                         "response_time": total_time * 1000,
#                         "exception": Exception(f"Failed job"),
#                         "response_length": 0
#                     }
#                 )
#             else:
#                 print(f"RESULT JOB_ID {job_id}: {result}")
#                 queue_eventos.put(
#                     {
#                         "request_type": "smart_contract_interaction",
#                         "name": "submit_job_and_get_result",
#                         "response_time": total_time * 1000,
#                         "exception": None,
#                         "response_length": result["charCount"],
#                         "context": {}
#                     }
#                 )
#             print(f"Total time for job {job_id}: {total_time} seconds")
#             return

#         current_time = time.time() - start_time
#         if current_time > timeout:
#             queue_eventos.put(
#                 {
#                     "request_type": "smart_contract_interaction",
#                     "name": "submit_job_and_get_result",
#                     "response_time": total_time * 1000,
#                     "exception": Exception(f"Timeout: Job {job_id} result not received within {timeout} seconds"),
#                     "response_length": 0
#                 }
#             )
#             return

#         await asyncio.sleep(0.1)

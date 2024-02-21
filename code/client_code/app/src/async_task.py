import uuid
from src.smart_contract import get_contract
import time
import asyncio

MAX_JOBS_RUN = 60
JOBS_SENT = 0
DICT_STARTING_TIMES = {}
LOCK = asyncio.Lock()


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
                print(f"ENVIO DE {JOBS_SENT} JOBS FINALIZADO EM: {time.time() - start_time}s")
                break
            await asyncio.sleep(0.1)
    finally:
        await asyncio.gather(*tasks)
        queue_eventos.put(DICT_STARTING_TIMES)

async def submit_job_and_get_result(user_count, job_id):
    contract = get_contract(user_count)  # Get the smart contract instance

    # Start measuring time
    start_time = time.time()

    # Submit a job
    try:
        contract.submitJob('https://pgc-yan-bucket.s3.us-east-2.amazonaws.com/output.pdf',
                            synchronous=False)
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

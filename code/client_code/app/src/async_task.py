import uuid
from src.smart_contract import get_contract
import time
import asyncio


def async_thread(queue_requests, queue_eventos):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(poller_loop(queue_requests, queue_eventos))


async def poller_loop(queue_requests, queue_eventos):
    while True:
        while not queue_requests.empty():
            asyncio.create_task(submit_job_and_get_result(queue_requests.get(), queue_eventos))
        await asyncio.sleep(0.1)


async def submit_job_and_get_result(user_count, queue_eventos):
    contract = get_contract(user_count)  # Get the smart contract instance

    # Start measuring time
    start_time = time.time()
    timeout = 600  # Set a timeout (in seconds)

    # Submit a job
    job_id = await asyncio.get_running_loop().run_in_executor(None,
                                                              contract.submitJob,
                                                              'https://www.teses.usp.br/teses/disponiveis/3/3141/tde-04012018-111326/publico/VladimirEmilianoMoreiraRochaCorr17.pdf')

    # Wait for the result with timeout
    while True:
        result = await asyncio.get_running_loop().run_in_executor(None,
                                                                  contract.getResult,
                                                                  job_id)
        if result['message']:
            end_time = time.time()
            total_time = end_time - start_time
            if result['message'] != 'SUCESSO':
                queue_eventos.put(
                    {
                        "request_type": "smart_contract_interaction",
                        "name": "submit_job_and_get_result",
                        "response_time": total_time * 1000,
                        "exception": Exception(f"Failed job"),
                        "response_length": 0
                    }
                )
            else:
                queue_eventos.put(
                    {
                        "request_type": "smart_contract_interaction",
                        "name": "submit_job_and_get_result",
                        "response_time": total_time * 1000,
                        "exception": None,
                        "response_length": result["charCount"],
                        "context": {}
                    }
                )
            print(f"Total time for job {job_id}: {total_time} seconds")
            return

        current_time = time.time() - start_time
        if current_time > timeout:
            queue_eventos.put(
                {
                    "request_type": "smart_contract_interaction",
                    "name": "submit_job_and_get_result",
                    "response_time": total_time * 1000,
                    "exception": Exception(f"Timeout: Job {job_id} result not received within {timeout} seconds"),
                    "response_length": 0
                }
            )
            return

        await asyncio.sleep(0.1)


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

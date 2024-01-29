import time

from src.smart_contract import get_contract


def event_thread(queue, fire_method):
    while True:
        if not queue.empty():
            starting_times = queue.get()
            break

        time.sleep(0.1)
    
    max_id = max(starting_times.keys())

    result = {}
    while not result.get("message"):
        result = get_contract(1).getResult(max_id)
        time.sleep(0.1)

    for id_job in starting_times.keys():
        result = get_contract(1).getResult(id_job)
        processed_time = get_contract(1)._execute_call_method('jobProcessingInfo', id_job)[1]
        if result['message'] != 'SUCESSO':
            fire_method(
                **{
                    "request_type": "smart_contract_interaction",
                    "name": "submit_job_and_get_result",
                    "response_time": (processed_time - starting_times[id_job]) * 1000,
                    "exception": Exception(f"Failed job"),
                    "response_length": 0
                }
            )
        else:
            fire_method(
                **{
                    "request_type": "smart_contract_interaction",
                    "name": "submit_job_and_get_result",
                    "response_time": (processed_time - starting_times[id_job]) * 1000,
                    "exception": None,
                    "response_length": result["charCount"],
                    "context": {}
                }
            )

            print(f"Total time for job {id_job}: {(processed_time - starting_times[id_job])} seconds")

import time

from src.smart_contract import get_contract


def event_thread(queue, fire_method):
    while True:
        if not queue.empty():
            valor = queue.get()
            if valor is None:
                break
            disparar_eventos(valor, fire_method)

        time.sleep(0.1)


def disparar_eventos(starting_times, fire_method):
    print(starting_times)
    max_id = max(starting_times.keys())

    result = {}
    while not result.get("message"):
        result = get_contract(999).getResult(max_id)
        time.sleep(0.1)

    for id_job in starting_times.keys():
        result = get_contract(999).getResult(id_job)
        processed_time = get_contract(999)._execute_call_method('jobProcessingInfo', id_job)[1]
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

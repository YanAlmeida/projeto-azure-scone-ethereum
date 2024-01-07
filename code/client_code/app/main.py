from locust import User, task, between, events
from src.smart_contract import get_contract  # Import your get_contract function
import time

class SmartContractUser(User):
    wait_time = between(1, 3)  # Define wait time between tasks

    @task
    def submit_job_and_get_result(self):
        contract = get_contract()  # Get the smart contract instance

        # Submit a job
        job_id = contract.submitJob('https://www.teses.usp.br/teses/disponiveis/3/3141/tde-04012018-111326/publico/VladimirEmilianoMoreiraRochaCorr17.pdf')  # Replace 'some_url' with actual URL

        # Start measuring time
        start_time = time.time()
        timeout = 600  # Set a timeout (in seconds)

        # Wait for the result with timeout
        while True:
            result = contract.getResult(job_id)
            if result['message']:
                end_time = time.time()
                total_time = end_time - start_time
                if result['message'] != 'SUCESSO':
                    events.request.fire(
                    request_type="smart_contract_interaction",
                    name="submit_job_and_get_result",
                    response_time=total_time*1000,  # Response time in milliseconds
                    exception=Exception(f"Failed job"),
                    response_length=0,  # Size of the response (in bytes)
                )
                events.request.fire(
                    request_type="smart_contract_interaction",
                    name="submit_job_and_get_result",
                    response_time=total_time*1000,
                    response_length=result["charCount"],
                    exception=None,
                    context={}
                )
                print(f"Total time for job {job_id}: {total_time} seconds")
                return 

            current_time = time.time() - start_time
            if  current_time > timeout:
                events.request.fire(
                    request_type="smart_contract_interaction",
                    name="submit_job_and_get_result",
                    response_time=current_time*1000,  # Response time in milliseconds
                    exception=Exception(f"Timeout: Job {job_id} result not received within {timeout} seconds"),
                    response_length=0,  # Size of the response (in bytes)
                )
                return

            time.sleep(0.5)  # Wait for a short period before checking again
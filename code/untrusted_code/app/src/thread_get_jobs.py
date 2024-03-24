from src.smart_contract import get_contract, Job
from typing import List
import os
import json
import asyncio
import aiohttp
import newrelic.agent
import traceback
from src.logger import LOGGER

TEE_ADDRESS = os.environ.get("TEE_ADDRESS")
CONNECTION_TUPLE = tuple(TEE_ADDRESS.split(":"))
SEMAPHORE = None
EVENT_LOOP = None


def start_event_loop():
    global SEMAPHORE
    global EVENT_LOOP
    EVENT_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(EVENT_LOOP)
    SEMAPHORE = asyncio.Semaphore(20)
    EVENT_LOOP.run_forever()


async def send_data_to_tee_async(job_id, data_chunks):
    # Cabeçalho e rodapé
    header = f"BEGIN#{job_id}##"
    footer = "#END_OF_TRANSMISSION#"

    reader, writer = await asyncio.open_connection(CONNECTION_TUPLE[0], int(CONNECTION_TUPLE[1]))

    # Envia o cabeçalho
    writer.write(header.encode("utf-8"))
    await writer.drain()

    # Envia os dados em pedaços
    for chunk in data_chunks:
        writer.write(chunk)
        await writer.drain()

    # Envia o rodapé
    writer.write(footer.encode("utf-8"))
    await writer.drain()

    data = await reader.read(1024)  # 1 KB

    writer.close()
    await writer.wait_closed()

    return data.decode("utf-8")


@newrelic.agent.background_task()
async def fetch_and_send_job(session: 'Session', job: Job):
    try:
        async with SEMAPHORE:
            async with session.get(job['fileUrl']) as response:
                response.raise_for_status()
                
                chunks = []
                async for chunk in response.content.iter_chunked(4096):
                    chunks.append(chunk)
                
                # Alteração aqui para incluir o ID do job
                total_response = await send_data_to_tee_async(job['jobId'], chunks)
                job = json.loads(total_response)
                    
    except Exception as e:
        exc_formatted = traceback.format_exc()
        LOGGER.warning(f"Erro ao processar o job {job['jobId']}: {exc_formatted}")
        job = {
            "jobId": job["jobId"],
            "message": "ERROR",
            "charCount": 0
        }
    return job

async def process_jobs(jobs: List[Job]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_send_job(session, job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


def get_and_process_jobs(jobs: List[Job]):
    """
    Função que gera Thread para recuperação dos Jobs no contrato
    :param jobs: lista de jobs
    :return:
    """

    def get_and_process_jobs_real():
        """
        Thread para recuperação dos Jobs no contrato, busca dos dados referenciados
        por ele e retorno à blockchain
        :return:
        """
        try:
            # get_contract().getJobsMachine(jobs)
            results = asyncio.run_coroutine_threadsafe(process_jobs(jobs), EVENT_LOOP).result()
            LOGGER.info(f"PROCESSOU JOBS DAS REQUISIÇÕES: {','.join([str(job['jobId']) for job in jobs])}")
            get_contract().submitResults(results)
        except Exception as e:
            exc_format = traceback.format_exc()
            LOGGER.error(exc_format)

    return get_and_process_jobs_real

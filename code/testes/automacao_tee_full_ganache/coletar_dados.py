import os
from typing import Tuple, List, Dict, Union, Any

from web3 import Web3, Account
from web3.contract import Contract
from web3.eth import Eth
from web3._utils.filters import LogFilter
from hdwallet import HDWallet
import threading
import asyncio

Job = Dict[str, Union[int, str]]
Result = Dict[str, Union[int, str]]


def get_account(index, mnemonic, derivation_path):
    wallet = HDWallet()
    wallet.from_mnemonic(mnemonic)
    wallet.from_path(f"{derivation_path}/{index}")
    return Account.from_key(wallet.private_key())


class SmartContract:
    _account: Account
    _contract: Contract
    _w3: Web3
    _event_job_submission_filter: LogFilter = None
    _nonce_lock = threading.Lock()

    def __init__(self, account: Account, contract: Contract, w3: Web3):
        """
        Método para instanciar classe SmartContract
        :param account: Objeto do tipo 'Account' representando
        conta utilizada pelo nó
        :param contract: Objeto do tipo 'Contract' representando
        o contrato inteligente
        :param w3: Objeto do tipo 'Web3' representando o cliente
        Web3 conectado à blockchain
        """
        self._account = account
        self._contract = contract
        self._w3 = w3
        self._nonce = self._w3.eth.get_transaction_count(self._account.address)

    def _execute_transaction_method(
            self, methodName: str, *args, synchronous=True, **kwargs
    ) -> Tuple[Any, Any]:
        """
        Método envio de transação/execução de função de escrita no contrato
        inteligente
        :param methodName: Nome da função a ser invocada
        :param args: Argumentos para enviar à função
        :param kwargs: Argumentos nomeados para enviar à função
        :return: Tupla de strings contendo hash da transação e sua receita
        """
        method = getattr(self._contract.functions, methodName)
        transaction = method(*args, **kwargs).build_transaction(
            {'gas': 1000000000, 'gasPrice': self._w3.to_wei('1', 'gwei'),
                "from": self._account.address, "nonce": self._nonce})
        signed_transaction = self._account.sign_transaction(transaction)
        transaction_hash = self._w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction)
        self._nonce += 1
        if synchronous:
            transaction_receipt = self._w3.eth.wait_for_transaction_receipt(
                transaction_hash)
            return (transaction_hash, transaction_receipt)
        return (transaction_hash, None)

    def _execute_call_method(
            self, methodName: str, *args, **kwargs
    ) -> Union[List, str, int]:
        """
        Método para execução de função read-only no contrato inteligente
        :param methodName: Nome da função a ser invocada
        :param args: Argumentos para enviar à função
        :param kwargs: Argumentos nomeados para enviar à função
        :return: Retorno da função em si (lista, string ou inteiro)
        """
        method = getattr(self._contract.functions, methodName)
        return method(*args, **kwargs).call({"from": self._account.address})

    def get_job_notification_filter(self) -> LogFilter:
        """
        Função para obtenção de LogFilter analisando eventos de
        alocação de jobs para a máquina no contrato inteligente
        :return: Objeto LogFilter para acesso aos eventos
        """
        if self._event_job_submission_filter is None:
            self._event_job_submission_filter = \
                self._contract.events.NotifyMachines.create_filter(
                    fromBlock='latest',
                    argument_filters={'_machine': self._account.address}
                )
        return self._event_job_submission_filter

    def submitJob(self, url: str, synchronous: bool = True) -> int:
        """
        Método para submissão de novo job
        :param url: URL contendo arquivo com os dados do job
        :return: Inteiro representando o ID do job criado no contrato
        inteligente
        """
        _, receipt = self._execute_transaction_method("submitJob", url,
                                                      synchronous=synchronous)
        if synchronous:
            logs = self._contract.events.ReturnUInt().process_receipt(receipt)
            return logs[0]['args']['_value']
        return

    def getResult(self, job_id: int) -> Result:
        """
        Método para recuperação de resultado de job
        :param job_id: ID do job cujo resultado será consultado
        :return: Objeto 'Result'
        """
        result = self._execute_call_method("getResult", job_id)
        return {"jobId": job_id, "charCount": result[0], "message": result[1]}
    
    def submitResults(self, results: List[Result]) -> Tuple[Any, Any]:
        """
        Método para envio de resultados de jobs à blockchain
        :param results: Lista de 'Result'
        :return: Hash e receita da transação
        """
        jobs_ids = [result["jobId"] for result in results]
        char_counts = [result["charCount"] for result in results]
        messages = [result["message"] for result in results]
        return self._execute_transaction_method("submitResults", jobs_ids,
                                            char_counts, messages, synchronous=True)
    def getJobs(self, id_list):
        result = self._execute_call_method("getJobs", id_list)
        jobs = [{"jobId": jobId, "fileUrl": fileUrl, "startingTimestamp": startingTimestamp, "processingTimestamp": processingTimestamp, "processedTimestamp": processedTimestamp} for jobId, fileUrl, startingTimestamp, processingTimestamp, processedTimestamp in zip(result[0], result[1], result[2], result[3], result[4])]
        return jobs

MNEMONIC_WORDS = os.environ.get("MNEMONIC",
                                "nation quality celery volume loan west master little expand card hire shell")
DERIVATION_PATH = os.environ.get("DERIVATION_PATH", "m/44'/60'/0'/0")
BLOCKCHAIN_ADDRESS = os.environ.get("BLOCKCHAIN_ADDRESS",
                                    "http://18.223.172.239:8545")
CONTRACT_ABI = os.environ.get("CONTRACT_ABI",
                              '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_machine","type":"address"},{"indexed":false,"internalType":"uint256","name":"_value","type":"uint256"}],"name":"ReturnUInt","type":"event"},{"inputs":[],"name":"collectResults","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"connectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"connectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disconnectMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"disconnectedMachines","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"idList","type":"uint256[]"}],"name":"getJobs","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"},{"internalType":"uint256[]","name":"startingTimes","type":"uint256[]"},{"internalType":"uint256[]","name":"processingTimes","type":"uint256[]"},{"internalType":"uint256[]","name":"endingTimes","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"}],"name":"getJobsMachine","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getJobsMachineView","outputs":[{"internalType":"uint256[]","name":"jobsIds","type":"uint256[]"},{"internalType":"string[]","name":"fileUrls","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"name":"getResult","outputs":[{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"heartBeat","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobProcessingInfo","outputs":[{"internalType":"uint256","name":"waitingTimestamp","type":"uint256"},{"internalType":"uint256","name":"processingTimestamp","type":"uint256"},{"internalType":"uint256","name":"currentStatus","type":"uint256"},{"internalType":"address","name":"responsibleMachine","type":"address"},{"internalType":"uint256","name":"indexInJobs","type":"uint256"},{"internalType":"uint256","name":"indexInMachine","type":"uint256"},{"internalType":"uint256","name":"processedTimestamp","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobProcessingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobUpdateInterval","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"jobWaitingMaxTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerAddress","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"jobsPerId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"string","name":"fileUrl","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastJobId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"processedJobs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"resetProcessedJobs","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"resultsPerJobId","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"uint256","name":"charCount","type":"uint256"},{"internalType":"string","name":"message","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"returnJobsIds","outputs":[{"internalType":"uint256[]","name":"jobIds","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bool","name":"value","type":"bool"}],"name":"setResultValue","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"url","type":"string"}],"name":"submitJob","outputs":[{"internalType":"uint256","name":"_jobId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string[]","name":"urls","type":"string[]"}],"name":"submitJobBatch","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"_jobsIds","type":"uint256[]"},{"internalType":"uint256[]","name":"_charCounts","type":"uint256[]"},{"internalType":"string[]","name":"_messages","type":"string[]"}],"name":"submitResults","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS",
                                  '0x5b92A0289CBeBacC143842122bC3c5B78e5584FB')

W3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_ADDRESS))

CONTRACT = {}


def get_contract(account_number) -> SmartContract:
    """
    Função para retorno de objeto para interação com o contrato inteligente.
    :return: Instância de 'SmartContract' (única na aplicação)
    """
    global CONTRACT
    if CONTRACT.get(account_number) is None:
        account = get_account(account_number, MNEMONIC_WORDS, DERIVATION_PATH)
        contract = W3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

        CONTRACT[account_number] = SmartContract(account, contract, W3)
    return CONTRACT[account_number]

def get_test_identifier(url):
    identifier = url.split('/')[-1].split('?')
    return identifier[0].strip('output_').strip('.pdf') + '-' + identifier[1]

from concurrent.futures import ThreadPoolExecutor

def split(list_a: list, chunk_size: int):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]

def get_jobs(chunk_size):
    jobs_ids = get_contract(999)._execute_call_method('returnJobsIds')

    pairs = split(jobs_ids, chunk_size)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(get_contract(999).getJobs, pair) for pair in pairs]

        # Optionally, wait for all futures to complete and process results
        final_result = []
        for future in futures:
            try:
                # Get the result of the future. This line will block until the future is complete
                final_result += future.result()
                # Process result (if needed)
            except Exception as e:
                print(f"Request failed: {e}")
        return final_result

from collections import defaultdict
from functools import partial
import json
import time

results = defaultdict(partial(defaultdict, list))
times = defaultdict(partial(defaultdict, int))

CHUNK_SIZE = 50

a = time.time()
jobs = get_jobs(CHUNK_SIZE)
print(time.time() - a)

for job in jobs:
    if job['processedTimestamp'] != 0:
        message = 'SUCESSO'
    else:
        message = 'ERRO'
    test_identifier = get_test_identifier(job['fileUrl'])
    
    results[test_identifier][message].append(job['processedTimestamp'] - job['startingTimestamp'])
    if times[test_identifier]['START'] == 0:
        times[test_identifier]['START'] = 1000000000000
    times[test_identifier]['START'] = min(times[test_identifier]['START'], job['startingTimestamp'])
    times[test_identifier]['END'] = max(times[test_identifier]['END'], job['processedTimestamp'])
print(len(jobs))

from datetime import datetime
import pytz

filename = f"/tmp/DADOS_TESTES.txt"

def timestamp_to_string(timestamp):
    datetime_value = datetime.fromtimestamp(timestamp, tz=pytz.timezone('America/Sao_Paulo'))
    return datetime_value.strftime("%Y-%m-%d %H:%M:%S")


with open(filename, 'a') as file:
    for test, tempos in times.items():
        for marcacao, tempo in tempos.items():
            file.write(f'{marcacao} {test}: {timestamp_to_string(tempo)}\n')
            if marcacao == 'END':
                file.write('#\n')

import json


filename = f"/tmp/{list(results.keys())[0]}/RESULTADOS_TESTES_BLOCKCHAIN.txt"

with open(filename, 'a') as file:
    file.write(json.dumps(results))


import requests
import json
import pytz
from datetime import datetime

API_KEY = 'API_KEY'
ACCOUNT_ID = 4269971
FUNCTION_NAME = 'OtherTransaction/Function/src.thread_accept_connection:process_pdf_data'

def query_trace_durations(starting_time: str, ending_time: str):
    """
    Queries New Relic for trace durations of a specific function within a specified time period.
    
    :param starting_time: The starting time of the period to query, in UTC-3 (São Paulo time)
    :param ending_time: The ending time of the period to query, in UTC-3 (São Paulo time)
    :return: JSON data of query results
    """
    # Convert São Paulo time (UTC-3) to UTC
    sao_paulo = pytz.timezone('America/Sao_Paulo')
    utc = pytz.utc

    start_dt = sao_paulo.localize(datetime.strptime(starting_time, '%Y-%m-%d %H:%M:%S')).astimezone(utc)
    end_dt = sao_paulo.localize(datetime.strptime(ending_time, '%Y-%m-%d %H:%M:%S')).astimezone(utc)

    # Format times in ISO 8601 format for the query
    start_time_utc = start_dt.timestamp() * 1000
    end_time_utc = end_dt.timestamp() * 1000
    
    # The GraphQL endpoint
    url = 'https://api.newrelic.com/graphql'

    # The query, using NRQL
    # Ensure your NRQL query is on a single line to avoid formatting issues
    nrql_query = f"FROM Transaction SELECT duration WHERE name = '{FUNCTION_NAME}' AND tags.accountId = '{ACCOUNT_ID}' SINCE {int(start_time_utc)} UNTIL {int(end_time_utc)} LIMIT 5000"
    
    # Construct the full GraphQL query
    query = {
      "query": f'''
        {{
          actor {{
            account(id: {ACCOUNT_ID}) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
      '''
    }

    # Headers with the API key
    headers = {
        'Content-Type': 'application/json',
        'API-Key': API_KEY,
    }

    # Sending the request
    response = requests.post(url, headers=headers, json=query)  # Use json parameter to automatically encode dict to JSON

    # Check response status
    if response.status_code == 200:
        # Return parsed JSON data
        return response.json()['data']['actor']['account']['nrql']['results']
    else:
        print("Failed to retrieve data:", response.status_code)
        return None

def process_text_to_dict_corrected(text):
    lines = text.strip().split('\n')
    test_dict = {}

    for line in lines:
        if line.startswith('START') or line.startswith('END'):
            parts = line.split(': ', 1)  # Correct split to include space
            key_value = parts[0].split(' ', 1)
            key = key_value[1].strip()
            if key not in test_dict:
                test_dict[key] = [None, None]
            if line.startswith('START'):
                test_dict[key][0] = parts[1].strip()
            else:
                test_dict[key][1] = parts[1].strip()

    # Convert list to tuple for final output
    for key in test_dict:
        test_dict[key] = tuple(test_dict[key])

    return test_dict

filename = "/tmp/DADOS_TESTES.txt"

with open(filename, 'r') as file:
    total_data = file.read()

tempos = process_text_to_dict_corrected(total_data)

resultados = {}
for k, v in tempos.items():
    resultados[k] = query_trace_durations(*v)

import json
import os


filename = f"/tmp/{list(tempos.keys())[0]}/RESULTADOS_TESTES_TEE.txt"

with open(filename, 'a') as file:
    file.write(json.dumps(resultados))
filename

os.rename("/tmp/DADOS_TESTES.txt", f"/tmp/{list(tempos.keys())[0]}/DADOS_TESTES.txt")

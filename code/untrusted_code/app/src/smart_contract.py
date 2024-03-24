import os
from typing import Tuple, List, Dict, Union, Any
import requests

Job = Dict[str, Union[int, str]]
Result = Dict[str, Union[int, str]]


class SmartContract:
    url = os.environ.get("BLOCKCHAIN_ADDRESS", "http://18.223.172.239:8545")
    account = os.environ.get("ACCOUNT_INDEX", '0')

    def heartBeat(self) -> int:
        pass

    def submitResults(self, results: List[Result]):
        response = requests.post(f"{self.url}/submit-result/", json=results)
        response.raise_for_status()
        return
    
    def pollJobs(self):
        response = requests.get(f"{self.url}/get-jobs-for-machine/{self.account}?limit={os.environ.get('LIMIT_JOBS', 100)}")
        response.raise_for_status()
        return response.json()['jobs']

    def connectMachine(self):
        response = requests.post(f"{self.url}/connect-machine/", json={'machine_id': self.account})
        response.raise_for_status()
        return


CONTRACT = None


def get_contract() -> SmartContract:
    """
    Função para retorno de objeto para interação com o contrato inteligente.
    :return: Instância de 'SmartContract' (única na aplicação)
    """
    global CONTRACT
    if CONTRACT is None:
        CONTRACT = SmartContract()
    return CONTRACT



def check_contract_available() -> bool:
    """
    Função para retorno de booleano indicando se o smart contract pode ser recuperado com sucesso
    """
    try:
        get_contract().pollJobs()
        return True
    except Exception as e:
        print(e)
        return False



# import os
# from typing import Tuple, List, Dict, Union, Any

# from web3 import Web3, Account
# from web3.contract import Contract
# from web3.eth import Eth
# from web3._utils.filters import LogFilter
# from hdwallet import HDWallet
# import threading
# import newrelic.agent
# import asyncio
# from src.logger import LOGGER
# import time


# Job = Dict[str, Union[int, str]]
# Result = Dict[str, Union[int, str]]

# def get_account(index, mnemonic, derivation_path):
#     wallet = HDWallet()
#     wallet.from_mnemonic(mnemonic)
#     wallet.from_path(f"{derivation_path}/{index}")
#     return Account.from_key(wallet.private_key())


# def split(list_a: list, chunk_size: int):
#     for i in range(0, len(list_a), chunk_size):
#         yield list_a[i:i + chunk_size]

# class SmartContract:
#     _account: Account
#     _contract: Contract
#     _w3: Web3
#     _event_job_submission_filter: LogFilter = None
#     _nonce = None
#     _nonce_lock = threading.Lock()
#     _jobs_seen = {}

#     def __init__(self, account: Account, contract: Contract, w3: Web3):
#         """
#         Método para instanciar classe SmartContract
#         :param account: Objeto do tipo 'Account' representando
#         conta utilizada pelo nó
#         :param contract: Objeto do tipo 'Contract' representando
#         o contrato inteligente
#         :param w3: Objeto do tipo 'Web3' representando o cliente
#         Web3 conectado à blockchain
#         """
#         self._account = account
#         self._contract = contract
#         self._w3 = w3
#         self._nonce = self._w3.eth.get_transaction_count(account.address)

#     def _execute_transaction_method(
#             self, methodName: str, *args, synchronous=True, **kwargs
#     ) -> Tuple[Any, Any]:
#         """
#         Método envio de transação/execução de função de escrita no contrato
#         inteligente
#         :param methodName: Nome da função a ser invocada
#         :param args: Argumentos para enviar à função
#         :param kwargs: Argumentos nomeados para enviar à função
#         :return: Tupla de strings contendo hash da transação e sua receita
#         """
#         with self._nonce_lock:
#             method = getattr(self._contract.functions, methodName)
#             transaction = method(*args, **kwargs).build_transaction(
#                 {'gas': 10000000, 'gasPrice': self._w3.to_wei('100', 'gwei'),
#                 "from": self._account.address, "nonce": self._nonce})
#             signed_transaction = self._account.sign_transaction(transaction)
#             transaction_hash = self._w3.eth.send_raw_transaction(
#                 signed_transaction.rawTransaction)
#             self._nonce += 1
#             if synchronous:
#                 transaction_receipt = self._w3.eth.wait_for_transaction_receipt(
#                     transaction_hash)
#                 return (transaction_hash, transaction_receipt)
#             return (transaction_hash, None)

#     def _execute_call_method(
#             self, methodName: str, *args, **kwargs
#     ) -> Union[List, str, int]:
#         """
#         Método para execução de função read-only no contrato inteligente
#         :param methodName: Nome da função a ser invocada
#         :param args: Argumentos para enviar à função
#         :param kwargs: Argumentos nomeados para enviar à função
#         :return: Retorno da função em si (lista, string ou inteiro)
#         """
#         method = getattr(self._contract.functions, methodName)
#         return method(*args, **kwargs).call({"from": self._account.address})

#     def connectMachine(self) -> Tuple[Any, Any]:
#         """
#         Método para conexão da máquina com a blockchain
#         :return: Hash e receita da transação em tupla
#         """
#         return self._execute_transaction_method("connectMachine")

#     def disconnectMachine(self) -> Tuple[Any, Any]:
#         """
#         Método para desconexão da máquina com a blockchain
#         :return: Hash e receita da transação em tupla
#         """
#         return self._execute_transaction_method("disconnectMachine")

#     def heartBeat(self) -> Tuple[Any, Any]:
#         """
#         Método para envio de heartbeat da máquina para a blockchain
#         :return: Hash e receita da transação em tupla
#         """
#         return self._execute_transaction_method("heartBeat", synchronous=False)
    
#     @newrelic.agent.background_task()
#     def getJobsMachineView(self) -> List[Job]:
#         result = self._execute_call_method("getJobsMachineView")
#         jobs_returned = [{"jobId": jobId, "fileUrl": fileUrl} for jobId, fileUrl in zip(result[0], result[1]) if jobId != 0]
        
#         return jobs_returned


#     @newrelic.agent.background_task()
#     def getJobsMachine(self, jobs_returned: List[Job]):
#         self._execute_transaction_method("getJobsMachine", [job['jobId'] for job in jobs_returned])
#         for job in jobs_returned:
#             if self._jobs_seen.get(job['jobId']):
#                 del self._jobs_seen[job['jobId']]
#         return jobs_returned

#     def pollJobs(self) -> List[Job]:
#         """
#         Método para recuperação dos jobs em espera alocados para a máquina
#         :return: Lista de 'Job'
#         """
#         jobs_returned = self.getJobsMachineView()
#         jobs = []
#         now = time.time()
#         for job in jobs_returned:
#             if now - self._jobs_seen.get(job['jobId'], 0) >= 600:
#                 self._jobs_seen[job['jobId']] = now
#                 jobs.append(job)
#                 continue

#         return jobs

#     @newrelic.agent.background_task()
#     def submitResults(self, results: List[Result], batch_size: int = 10) -> Tuple[Any, Any]:
#         """
#         Método para envio de resultados de jobs à blockchain
#         :param results: Lista de 'Result'
#         :return: Hash e receita da transação
#         """
#         results_batched = split(results, batch_size)

#         for results_batch in results_batched:
#             jobs_ids = [result["jobId"] for result in results_batch]
#             char_counts = [result["charCount"] for result in results_batch]
#             messages = [result["message"] for result in results_batch]
#             self._execute_transaction_method("submitResults", jobs_ids,
#                                                 char_counts, messages, synchronous=False)


# MNEMONIC_WORDS = os.environ.get("MNEMONIC")
# DERIVATION_PATH = os.environ.get("DERIVATION_PATH")
# BLOCKCHAIN_ADDRESS = os.environ.get("BLOCKCHAIN_ADDRESS")
# CONTRACT_ABI = os.environ.get("CONTRACT_ABI")
# CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")
# ACCOUNT_INDEX = os.environ.get("ACCOUNT_INDEX", 0)

# W3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_ADDRESS))

# CONTRACT = None


# def get_contract() -> SmartContract:
#     """
#     Função para retorno de objeto para interação com o contrato inteligente.
#     :return: Instância de 'SmartContract' (única na aplicação)
#     """
#     global CONTRACT
#     if CONTRACT is None:
#         account = get_account(ACCOUNT_INDEX, MNEMONIC_WORDS, DERIVATION_PATH)
#         contract = W3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#         CONTRACT = SmartContract(account, contract, W3)
#     return CONTRACT


# def check_contract_available() -> bool:
#     """
#     Função para retorno de booleano indicando se o smart contract pode ser recuperado com sucesso
#     """
#     try:
#         get_contract()
#         return True
#     except Exception as e:
#         print(e)
#         return False

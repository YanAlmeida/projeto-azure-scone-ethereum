import os
from typing import Tuple, List, Dict, Union, Any

from web3 import Web3, Account
from web3.contract import Contract
from web3.eth import Eth
from web3._utils.filters import LogFilter
from hdwallet import HDWallet
import threading
import newrelic.agent
import asyncio


Job = Dict[str, Union[int, str]]
Result = Dict[str, Union[int, str]]


def split(list_a: list, chunk_size: int):
  for i in range(0, len(list_a), chunk_size):
    yield list_a[i:i + chunk_size]


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
    _nonce = None
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
        self._nonce = self._w3.eth.get_transaction_count(account.address)

    async def _execute_transaction_method_asyncio(self, method_name: str, *args, **kwargs):
        result = await asyncio.get_running_loop().run_in_executor(None, self._execute_transaction_method, method_name, *args, **kwargs)
        return result

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
        with self._nonce_lock:
            method = getattr(self._contract.functions, methodName)
            transaction = method(*args, **kwargs).build_transaction(
                {'gas': 2000000, 'gasPrice': self._w3.to_wei('100', 'gwei'),
                "from": self._account.address, "nonce": self._nonce})
            signed_transaction = self._account.sign_transaction(transaction)
            try:
                transaction_hash = self._w3.eth.send_raw_transaction(
                    signed_transaction.rawTransaction)
            except:
                self._nonce = self._w3.eth.get_transaction_count(self._account.address)
                transaction = method(*args, **kwargs).build_transaction(
                    {'gas': 2000000, 'gasPrice': self._w3.to_wei('100', 'gwei'),
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
        return method(*args, **kwargs).call()

    def connectMachine(self) -> Tuple[Any, Any]:
        """
        Método para conexão da máquina com a blockchain
        :return: Hash e receita da transação em tupla
        """
        return self._execute_transaction_method("connectMachine")

    def disconnectMachine(self) -> Tuple[Any, Any]:
        """
        Método para desconexão da máquina com a blockchain
        :return: Hash e receita da transação em tupla
        """
        return self._execute_transaction_method("disconnectMachine")

    def heartBeat(self) -> Tuple[Any, Any]:
        """
        Método para envio de heartbeat da máquina para a blockchain
        :return: Hash e receita da transação em tupla
        """
        return self._execute_transaction_method("heartBeat", synchronous=False)
    
    async def _getJobsMachine_asyncio(self, batch_size: int = 100):
        result = self._execute_call_method("getJobsMachineView")
        jobs_returned = [{"jobId": jobId, "fileUrl": fileUrl} for jobId, fileUrl in zip(result[0], result[1]) if jobId != 0]
        jobs_batched = split(jobs_returned, batch_size)

        async_tasks = []
        if jobs_returned:
            for jobs_batch in jobs_batched:
                task = self._execute_transaction_method_asyncio("getJobsMachine", [job['jobId'] for job in jobs_batch])
                async_tasks.append(task)
            await asyncio.gather(*async_tasks)
        return jobs_returned

    @newrelic.agent.background_task()
    def getJobsMachine(self, batch_size: int = 100) -> List[Job]:
        """
        Método para recuperação dos jobs em espera alocados para a máquina
        :return: Lista de 'Job'
        """
        return asyncio.run(self._getJobsMachine_asyncio(batch_size))

    @newrelic.agent.background_task()
    def submitResults(self, results: List[Result], batch_size: int = 10) -> Tuple[Any, Any]:
        """
        Método para envio de resultados de jobs à blockchain
        :param results: Lista de 'Result'
        :return: Hash e receita da transação
        """
        results_batched = split(results, batch_size)

        for results_batch in results_batched:
            jobs_ids = [result["jobId"] for result in results_batch]
            char_counts = [result["charCount"] for result in results_batch]
            messages = [result["message"] for result in results_batch]
            self._execute_transaction_method("submitResults", jobs_ids,
                                                char_counts, messages, synchronous=False)


MNEMONIC_WORDS = os.environ.get("MNEMONIC")
DERIVATION_PATH = os.environ.get("DERIVATION_PATH")
BLOCKCHAIN_ADDRESS = os.environ.get("BLOCKCHAIN_ADDRESS")
CONTRACT_ABI = os.environ.get("CONTRACT_ABI")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")
ACCOUNT_INDEX = os.environ.get("ACCOUNT_INDEX", 0)

W3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_ADDRESS))

CONTRACT = None


def get_contract() -> SmartContract:
    """
    Função para retorno de objeto para interação com o contrato inteligente.
    :return: Instância de 'SmartContract' (única na aplicação)
    """
    global CONTRACT
    if CONTRACT is None:
        account = get_account(ACCOUNT_INDEX, MNEMONIC_WORDS, DERIVATION_PATH)
        contract = W3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

        CONTRACT = SmartContract(account, contract, W3)
    return CONTRACT


def check_contract_available() -> bool:
    """
    Função para retorno de booleano indicando se o smart contract pode ser recuperado com sucesso
    """
    try:
        get_contract()
        return True
    except Exception as e:
        print(e)
        return False

import os
from typing import Tuple, List, Dict, Union, Any

from web3 import Web3, Account
from web3.contract import Contract
from hdwallet import HDWallet

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

    def __init__(self, account: Account, contract: Contract, w3: Web3):
        self._account = account
        self._contract = contract
        self._w3 = w3

    def _execute_transaction_method(
            self, methodName: str, *args, **kwargs
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
        nonce = self._w3.eth.get_transaction_count(self._account.address)
        transaction = method(*args, **kwargs).build_transaction(
            {'gas': 1000000, 'gasPrice': self._w3.to_wei('1', 'gwei'),
             "from": self._account.address, "nonce": nonce})
        signed_transaction = self._account.sign_transaction(transaction)
        transaction_hash = self._w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction)
        transaction_receipt = self._w3.eth.wait_for_transaction_receipt(
            transaction_hash)
        return transaction_hash, transaction_receipt

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

    def submitJob(self, url: str) -> int:
        """
        Método para submissão de novo job
        :param url: URL contendo arquivo com os dados do job
        :return: Inteiro representando o ID do job criado no contrato
        inteligente
        """
        _, receipt = self._execute_transaction_method("submitJob", url)
        logs = self._contract.events.ReturnUInt().process_receipt(receipt)
        return logs[0]['args']['_value']

    def getJobs(self) -> List[Job]:
        """
        Método para recuperação de todos os jobs armazenados na blockchain
        :return: Lista de 'Job'
        """
        result = self._execute_call_method("getJobs")
        return [{"jobId": jobId, "fileUrl": fileUrl} for jobId, fileUrl in
                zip(result[0], result[1])]

    def getResult(self, job_id: int) -> Result:
        """
        Método para recuperação de resultado de job
        :param job_id: ID do job cujo resultado será consultado
        :return: Objeto 'Result'
        """
        result = self._execute_call_method("getResult", job_id)
        return {"jobId": job_id, "charCount": result[0], "message": result[1]}


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

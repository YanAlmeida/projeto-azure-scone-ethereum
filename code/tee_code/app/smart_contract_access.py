import os
from web3 import Web3, Account
from web3.contract import Contract
from web3.eth import Eth
from hdwallet import HDWallet

class SmartContract:
    
    _account: Account
    _contract: Contract
    _w3: Web3
    
    def __init__(self, account: Account, contract: Contract, w3: Web3):
        self._account = account
        self._contract = contract
        self._w3 = w3
    
    def _execute_transaction_method(self, methodName: str, *args, **kwargs) -> str:
        method = getattr(self._contract.functions, methodName)
        nonce = self._w3.eth.get_transaction_count(self._account.address)
        transaction = method(*args, **kwargs).build_transaction({'gas': 1000000, 'gasPrice': self._w3.to_wei('1', 'gwei'), "from": self._account.address, "nonce": nonce})
        signed_transaction = self._account.sign_transaction(transaction)
        transaction_hash = self._w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        transaction_receipt = self._w3.eth.wait_for_transaction_receipt(transaction_hash)
        return (transaction_hash, transaction_receipt)

    def _execute_call_method(self, methodName: str, *args, **kwargs) -> str:
        method = getattr(self._contract.functions, methodName)
        return method(*args, **kwargs).call()
        


MNEMONIC_WORDS = os.environ.get("MNEMONIC")
DERIVATION_PATH = os.environ.get("DERIVATION_PATH")
BLOCKCHAIN_ADDRESS = os.environ.get("BLOCKCHAIN_ADDRESS")
CONTRACT_ABI = os.environ.get("CONTRACT_ABI")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")

WALLET = HDWallet()
WALLET.from_mnemonic(MNEMONIC_WORDS)
WALLET.from_path(DERIVATION_PATH)

W3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_ADDRESS))


def main():
    account = Account.from_key(WALLET.private_key())
    contract = W3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    smartContract = SmartContract(account, contract, W3)
    smartContract._execute_transaction_method("setData", "pesadsadra")
    print(smartContract._execute_call_method("getData"))
    

if __name__ == "__main__":
    main()

import os
from web3 import Web3, Account
from web3.contract import Contract
from mnemonic import Mnemonic
from hdwallet import HDWallet

class SmartContract:
    
    _account: Account
    _contract: Contract
    
    def __init__(self, account: Account, contract: Contract):
        self._account = account
        self._contract = contract


MNEMONIC_WORDS = os.environ.get("MNEMONIC")
BLOCKCHAIN_ADDRESS = os.environ.get("BLOCKCHAIN_ADDRESS")
CONTRACT_ABI = os.environ.get("CONTRACT_ABI")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")

MNEMO = Mnemonic.to_seed(MNEMONIC_WORDS, passphrase="")
WALLET = HDWallet()
WALLET.from_seed(MNEMO.hex())

W3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_ADDRESS))


def main():
    account = Account.from_key(WALLET.private_key())
    contract = W3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    smartContract = SmartContract(account, contract)
    print(smartContract.__dict__)

if __name__ == "__main__":
    main()
        

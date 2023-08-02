from web3 import Web3, Account

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider('http://ip_of_blockchain_instance:8545'))

# Get the account information
private_key = 'YOUR_PRIVATE_KEY'
account = Account.privateKeyToAccount(private_key)

# ABI and address of the smart contract
contract_abi = '[ABI_HERE]'
contract_address = '0xAddressOfYourSmartContract'

# Create contract object
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Read data from the contract (replace 'data' with the actual function you want to call)
data = contract.functions.data().call()

print('Data from smart contract:', data)
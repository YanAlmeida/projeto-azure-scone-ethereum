const { Web3 } = require('web3');
const HDWalletProvider = require('@truffle/hdwallet-provider');
const fs = require('fs');

const mnemonic = process.env.MNEMONIC; // get the mnemonic from environment variables
const provider = new HDWalletProvider(mnemonic, 'http://0.0.0.0:8545');

const web3 = new Web3(provider);

const contractBasePath = process.argv[2];
const contractName = process.argv[3];
const contractOutputFile = process.argv[4];

let contractData = JSON.parse(fs.readFileSync(contractOutputFile, 'utf8'));

let abi = contractData.contracts[`${contractBasePath}:${contractName}`].abi;
let bytecode = '0x' + contractData.contracts[`${contractBasePath}:${contractName}`].bin;

let myContract = new web3.eth.Contract(abi);

web3.eth.getAccounts().then(function(accounts) {
    myContract.deploy({
        data: bytecode
    }).send({
        from: accounts[0],
        gas: '4700000'
    }).then(function(newContractInstance) {
        console.log('Contract Address: ', newContractInstance.options.address);
        console.log('Contract ABI: ', JSON.stringify(abi))
    }).catch(function(error) {
        console.error('Error during contract deployment:', error);
    });
}).catch(function(error) {
    console.error('Error getting accounts:', error);
});

# Use the official Solidity compiler image to get solc
FROM ethereum/solc:0.8.9 AS solc

# Use the official Go Ethereum image as the base image
FROM node:16

# Copy the Solidity compiler from the solc stage
COPY --from=solc /usr/bin/solc /usr/bin/solc

# Verify the installation
RUN solc --version

# Installing web3 js
RUN npm install web3@4.0.3 --prefix /scripts

# Install @truflle/hdwallet-provider
RUN npm install @truffle/hdwallet-provider@2.1.13 --prefix /scripts

# Install Ganache CLI
RUN npm install -g ganache-cli@6.12.2

# Create directory for the compiled contract
RUN mkdir -p contractOutput

# Copy the contract, the deployment code and deployment script
COPY contracts/smartContract.sol /contracts/smartContract.sol
COPY deploy.js /scripts/deploy.js
COPY deployContract.sh /scripts/deployContract.sh

# Make the script executable
RUN chmod +x /scripts/deployContract.sh

# Compile the contract
RUN solc --combined-json abi,bin /contracts/smartContract.sol > /contractOutput/smartContract.json

# Set the working directory inside the container
WORKDIR /usr/src/app

# Expose the port Ganache CLI will run on
EXPOSE 8545

# Deterministic mnemonic and derivation path
ENV MNEMONIC="nation quality celery volume loan west master little expand card hire shell"
ENV DERIVATION_PATH="m/44'/60'/0'/0/0"

# Initial balance for the accounts in Wei
ENV INITIAL_BALANCE="1000000000000000"

# Run Ganache CLI with the specified mnemonic and balance when the container launches
ENTRYPOINT [ "/scripts/deployContract.sh" ]

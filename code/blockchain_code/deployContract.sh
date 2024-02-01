#!/bin/sh

# Start Ganache in the background
ganache --server.host 0.0.0.0 --wallet.mnemonic "${MNEMONIC}" --wallet.hdPath "${DERIVATION_PATH}" --wallet.defaultBalance "${INITIAL_BALANCE}" -a 1000 --miner.blockTime 15 --miner.blockGasLimit 0x1C9C380 --miner.defaultGasPrice 0x174876e800 &

# Wait for Ganache to initialize
echo "Waiting for Ganache to initialize..."
until curl -s http://0.0.0.0:8545 >/dev/null; do
  echo "Waiting for Ganache..."
  sleep 1
done

# Run the deployment script
node /scripts/deploy.js contracts/smartContract.sol smartContract /contractOutput/smartContract.json

#!/bin/sh

# Start Ganache in the background
ganache-cli --host 0.0.0.0 --mnemonic "${MNEMONIC}" --derive-path "${DERIVATION_PATH}" --defaultBalanceEther "${INITIAL_BALANCE}" -a 1000 --blockTime 15 --gasLimit 0x1C9C380 &

# Wait for Ganache to initialize
echo "Waiting for Ganache to initialize..."
until curl -s http://0.0.0.0:8545 >/dev/null; do
  echo "Waiting for Ganache..."
  sleep 1
done

# Run the deployment script
node /scripts/deploy.js contracts/smartContract.sol smartContract /contractOutput/smartContract.json

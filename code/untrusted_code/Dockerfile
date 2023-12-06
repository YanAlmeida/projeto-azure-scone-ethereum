FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

COPY ./app /app

ENV MNEMONIC="candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
ENV DERIVATION_PATH="m/44'/60'/0'/0/0"
ENV BLOCKCHAIN_ADDRESS="address://address:8080"
ENV CONTRACT_ABI="0x000"
ENV CONTRACT_ADDRESS="0x000"
ENV ACCOUNT_INDEX=0
ENV TEE_ADDRESS = "127.0.0.1:9090"

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]

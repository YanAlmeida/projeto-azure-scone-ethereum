FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

COPY ./app /app


ENV WRITE_PIPE_PATH="/tmp/named_pipes/write_pipe"
ENV READ_PIPE_PATH="/tmp/named_pipes/read_pipe"
ENV MNEMONIC="candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
ENV DERIVATION_PATH="m/44'/60'/0'/0/0"
ENV BLOCKCHAIN_ADDRESS="address://address:8080"
ENV CONTRACT_ABI="0x000"
ENV CONTRACT_ADDRESS="0x000"
ENV ACCOUNT_INDEX=0

RUN pip install -r /app/requirements.txt

VOLUME /tmp/named_pipes

ENTRYPOINT ["python3", "/app/main.py"]

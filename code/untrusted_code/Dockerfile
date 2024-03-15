FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

COPY ./app /app

ENV MNEMONIC="nation quality celery volume loan west master little expand card hire shell"
ENV DERIVATION_PATH="m/44'/60'/0'/0"
ENV BLOCKCHAIN_ADDRESS="address://address:8080"
ENV CONTRACT_ABI="0x000"
ENV CONTRACT_ADDRESS="0x000"
ENV ACCOUNT_INDEX=0
ENV TEE_ADDRESS="127.0.0.1:9090"
ENV NEW_RELIC_CONFIG_FILE="/app/newrelic.ini"
ENV NEW_RELIC_INFINITE_TRACING_SPAN_QUEUE_SIZE=100000


RUN pip3 install -r /app/requirements.txt
RUN pip3 install newrelic
RUN newrelic-admin validate-config /app/newrelic.ini

ENTRYPOINT ["newrelic-admin", "run-program", "python3", "/app/main.py"]

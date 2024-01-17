FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

EXPOSE 9090

COPY ./app /app

ENV NEW_RELIC_CONFIG_FILE="/app/newrelic.ini"

RUN pip3 install newrelic
RUN newrelic-admin validate-config /app/newrelic.ini

ENTRYPOINT ["newrelic-admin", "run-program", "python3", "/app/main.py"]

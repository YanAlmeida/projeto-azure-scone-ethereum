FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

COPY ./src /app
ENTRYPOINT ["python3", "/app/untrusted_test.py"]
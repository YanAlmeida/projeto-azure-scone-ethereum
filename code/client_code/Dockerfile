FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

RUN pip3 install locust==2.19.1

COPY . /app

RUN pip3 install -r /app/requirements.txt

ENV BLOCKCHAIN_ADDRESS="13.59.79.73"

EXPOSE 8089

ENTRYPOINT ["locust", "-f", "/app/main.py"]

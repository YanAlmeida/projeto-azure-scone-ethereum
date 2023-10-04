FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

COPY ./src /app

RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]

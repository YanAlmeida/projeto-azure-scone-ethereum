FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

EXPOSE 9090

COPY ./app /app
ENTRYPOINT ["python3", "/app/main.py"]

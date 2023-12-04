FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip

ENV READ_PIPE_PATH="/tmp/named_pipes/write_pipe"
ENV WRITE_PIPE_PATH="/tmp/named_pipes/read_pipe"

VOLUME /tmp/named_pipes

COPY ./app /app
ENTRYPOINT ["python3", "/app/main.py"]

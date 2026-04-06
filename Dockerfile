FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    procps \
    grep \
    gawk \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pydantic pydantic-core

CMD ["tail", "-f", "/dev/null"]
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    procps \
    grep \
    gawk \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

# Here is the updated line with fastapi and uvicorn:
RUN pip install --no-cache-dir pydantic pydantic-core fastapi uvicorn

EXPOSE 7860

CMD ["python", "-u", "health_server.py"]
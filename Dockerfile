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


# Expose the port Hugging Face expects
EXPOSE 7860

# Run a tiny built-in server to pass the health check
CMD ["python", "-m", "http.server", "7860"]
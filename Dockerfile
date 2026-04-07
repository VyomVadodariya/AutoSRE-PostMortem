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


# (Keep all your other lines the same)

EXPOSE 7860

# The bulletproof Hugging Face health-check server
CMD ["python", "-u", "-m", "http.server", "7860", "--bind", "0.0.0.0"]
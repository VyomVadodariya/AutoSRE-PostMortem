FROM python:3.11-slim

# Install system tools your SRE environment needs (procps, grep, etc.)
RUN apt-get update && apt-get install -y \
    procps \
    grep \
    gawk \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# IMPORTANT: Create the workspace folder so your code doesn't crash
RUN mkdir -p /app/sre_workspace

COPY . /app

# Install all OpenEnv and FastAPI dependencies
RUN pip install --no-cache-dir \
    pydantic \
    pydantic-core \
    fastapi \
    uvicorn \
    requests \
    openenv-core \
    python-multipart

EXPOSE 7860

# Force logs to show up instantly so we can see any future errors
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "health_server.py"]
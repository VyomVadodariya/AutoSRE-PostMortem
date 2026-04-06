# Use a lightweight Python Linux image
FROM python:3.11-slim

# Install the essential Linux terminal tools the AI will use
RUN apt-get update && apt-get install -y \
    procps \
    grep \
    gawk \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory inside the cloud container
WORKDIR /app

# Copy all your local files into the cloud container
COPY . /app

# Install the Python requirements
RUN pip install --no-cache-dir pydantic openenv-py

# The Hugging Face OpenEnv validator handles the boot command automatically.
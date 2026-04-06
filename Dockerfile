# Use a lightweight Python Linux image
FROM python:3.11-slim

# Install the essential Linux terminal tools
RUN apt-get update && apt-get install -y \
    procps \
    grep \
    gawk \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy everything (including our custom 'openenv' folder)
COPY . /app

# Install only the necessary public packages
# We removed openenv-py because we provide the logic in our local folder
RUN pip install --no-cache-dir pydantic pydantic-core

# The Hugging Face OpenEnv validator handles the rest
# ... (all your previous lines remain the same) ...

# Keep the container running so it doesn't exit immediately
CMD ["tail", "-f", "/dev/null"]
FROM python:3.11-slim

# (Keep the FROM and apt-get lines at the top the same)

# Install EVERYTHING your environment.py imports
RUN pip install --no-cache-dir \
    pydantic \
    pydantic-core \
    fastapi \
    uvicorn \
    requests \
    openenv \
    python-multipart

# (Keep WORKDIR, COPY, EXPOSE, and CMD the same)

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pydantic pydantic-core


# (Keep all your other lines the same)

EXPOSE 7860

# Run our custom SRE health check server
CMD ["python", "-u", "health_server.py"]
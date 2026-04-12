FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face requires port 7860
EXPOSE 7860

# Boot up the FastAPI server for the automated grader
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "AutoSRE server is running"}

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
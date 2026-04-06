from fastapi import FastAPI
from environment import AutoSREEnvironment

app = FastAPI()
env = AutoSREEnvironment()

@app.get("/")
def read_root():
    return {"status": "Running", "project": "AutoSRE-PostMortem"}

@app.post("/step")
def take_step(action: dict):
    # This is a simplified endpoint for the hackathon UI
    return {"message": "Action received"}

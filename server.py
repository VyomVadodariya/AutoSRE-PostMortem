from fastapi import FastAPI, Request
from pydantic import BaseModel
from sre_env import SREEnvironment

app = FastAPI()
env = SREEnvironment()

class StepRequest(BaseModel):
    action: str

@app.post("/reset")
async def reset(request: Request):
    """Scaler Bot calls this to start. Safely ignores hidden grader payloads."""
    try:
        await request.json() 
    except:
        pass
    obs = env.reset()
    return {"observation": obs}

@app.post("/step")
def step(req: StepRequest):
    """Scaler Bot calls this to take an action"""
    obs, reward, done = env.step(req.action)
    return {"observation": obs, "reward": reward, "done": done}
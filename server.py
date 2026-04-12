from fastapi import FastAPI, Request
from pydantic import BaseModel
from sre_env import SREEnvironment

app = FastAPI()
env = SREEnvironment()

class StepRequest(BaseModel):
    action: str

@app.get("/tasks")
def get_tasks():
    """Tells the Phase 2 Grader that we have 3 distinct tasks to evaluate."""
    return {
        "task_1": {"name": "Malware Spike", "description": "Fix high CPU"},
        "task_2": {"name": "Log Bloat", "description": "Fix full disk"},
        "task_3": {"name": "Hybrid Failure", "description": "Fix both issues"}
    }

@app.post("/reset")
async def reset(request: Request):
    """Scaler Bot calls this to start. Now supports task selection."""
    task_id = None
    try:
        data = await request.json()
        task_id = data.get("task_id")
    except:
        pass
    
    obs = env.reset(task_id=task_id)
    return {"observation": obs}

@app.post("/step")
def step(req: StepRequest):
    """Scaler Bot calls this to take an action"""
    obs, reward, done = env.step(req.action)
    return {"observation": obs, "reward": reward, "done": done}
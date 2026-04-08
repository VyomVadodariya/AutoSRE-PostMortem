import sys
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn

# --- 1. BOOT DIAGNOSTICS ---
try:
    print("--- Attempting to load SRE Brain ---")
    from environment import SREEnvironment
    from models import SREAction 
    import generate_logs
    print("✅ All modules loaded successfully!")
except Exception as e:
    print(f"❌ FATAL BOOT ERROR: {str(e)}")
    sys.exit(1)

# --- 2. INITIALIZATION ---
app = FastAPI(title="AutoSRE PostMortem V1")
env = SREEnvironment()

class ActionRequest(BaseModel):
    command: str

# --- 3. ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "🟢 AutoSRE Environment is LIVE and ready for AI agents."}

@app.get("/state")
def get_state():
    return {"health": env.system_health_score, "steps": env.step_count}

@app.post("/reset")
def reset_environment(task_id: str = Query("3", description="The scenario ID to load")):
    print(f"\n[START] Starting Task {task_id}")
    obs = env.reset(task_id=task_id)
    return {"observation": obs.terminal_output}

@app.post("/step")
def take_action(req: ActionRequest):
    try:
        print(f"\n[STEP] AI Action: {req.command}")
        
        # Create the action your Environment expects
        action = SREAction(
            action_type="bash_command", 
            command=req.command
        )
        
        result = env.step(action)
        print(f"Current Reward: {result.reward}")
        
        return {
            "observation": str(result.observation.terminal_output),
            "health_score": float(result.observation.system_health_score),
            "reward": float(result.reward),
            "done": bool(result.done)
        }
    except Exception as e:
        print(f"❌ STEP ERROR: {str(e)}")
        return {"error": str(e)}, 500

# --- 4. START SERVER ---
if __name__ == "__main__":
    print("🚀 Starting Uvicorn Server on Port 7860...")
    uvicorn.run(app, host="0.0.0.0", port=7860)
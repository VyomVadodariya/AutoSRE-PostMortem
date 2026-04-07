from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# TODO: Import your actual environment class here
# from environment import AutoSREEnv 

app = FastAPI(title="AutoSRE PostMortem V1")
# env = AutoSREEnv() # Initialize your world

# --- The input schemas for the AI ---
class Action(BaseModel):
    command: str

@app.get("/")
def health_check():
    return {"status": "🟢 AutoSRE Environment is LIVE and ready for AI agents."}

@app.post("/reset")
def reset_environment():
    # state = env.reset()
    # return {"observation": state}
    return {"observation": "ALERT: Incoming DDoS detected on Port 443. CPU at 99%."}

@app.post("/step")
def take_action(req: ActionRequest):
    try:
        # Create the action your Environment expects
        action = SREAction(
            action_type="bash_command", 
            command=req.command
        )
        
        # Execute the step
        result = env.step(action)
        
        # Return the results safely
        return {
            "observation": str(result.observation.terminal_output),
            "health_score": float(result.observation.system_health_score),
            "reward": float(result.reward),
            "done": bool(result.done)
        }
    except Exception as e:
        # This will print the EXACT error in your HF Logs if it fails again
        print(f"❌ STEP ERROR: {str(e)}")
        return {"error": str(e)}, 500
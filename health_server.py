from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# 1. Import YOUR actual environment and models
from environment import SREEnvironment
from models import SREAction 

app = FastAPI(title="AutoSRE PostMortem V1")

# 2. Initialize YOUR world
print("--- Booting Auto-SRE Engine ---")
env = SREEnvironment()

# The format the AI uses to send commands
class ActionRequest(BaseModel):
    command: str

@app.get("/")
def health_check():
    return {"status": "🟢 AutoSRE Environment is LIVE and ready for AI agents."}

@app.post("/reset")
def reset_environment():
    # Call your actual reset function (triggers generate_logs.py)
    obs = env.reset()
    
    # Send the pristine state back to the AI
    return {
        "observation": f"Environment Reset. Health: {obs.system_health_score}. Directory: {obs.current_directory}"
    }

@app.post("/step")
def take_action(req: ActionRequest):
    # 1. Format the AI's text into YOUR SREAction object
    action = SREAction(
        action_type="bash_command", 
        command=req.command
    )
    
    # 2. Run the command in your environment
    result = env.step(action)
    
    # 3. Send the terminal output and health back to the AI
    # (Using getattr as a failsafe just in case)
    terminal_out = getattr(result.observation, 'terminal_output', str(result.observation))
    health = getattr(result.observation, 'system_health_score', 0)
    reward_val = getattr(result, 'reward', 0)
    is_done = getattr(result, 'done', False)

    return {
        "observation": terminal_out,
        "health_score": health,
        "reward": reward_val,
        "done": is_done
    }

if __name__ == "__main__":
    print("--- Booting Uvicorn Enterprise Server ---")
    uvicorn.run(app, host="0.0.0.0", port=7860)
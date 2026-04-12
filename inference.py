import os
from openai import OpenAI
from sre_env import SREEnvironment

# 1. Initialize Proxy Connection (Hackathon safe!)
try:
    client = OpenAI(
        base_url=os.environ.get("API_BASE_URL"), 
        api_key=os.environ.get("API_KEY")
    )
except Exception as e:
    client = None

def run_agent():
    # MANDATORY: Start tag for the grader
    print("[START] task=Incident_Resolution", flush=True)

    if not client:
        # Failsafe if running locally without keys
        print("[END] task=Incident_Resolution score=0.1 steps=1", flush=True)
        return

    # 2. Initialize the Game Board (Your new environment)
    env = SREEnvironment()
    
    # 3. Give the AI the rulebook
    system_prompt = """You are an elite SRE agent. Investigate and restore the system.
    Available Commands: 
    - check_metrics
    - list_processes
    - inspect_logs
    - check_network
    - kill_process <pid>
    - clear_logs
    - restart_service nginx

    Strategy:
    - Diagnose before acting.
    - Some scenarios have MULTIPLE root causes (e.g., high CPU AND full disk).
    - Restore 'nginx' only after all threats are neutralized.
    Reply with ONLY the command string."""

    chat_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "ALERT: CPU at 99.9%. Begin investigation."}
    ]

    done = False
    
    try:
        # 4. The main Game Loop
        while not done:
            # AI decides its move
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
                temperature=0.1 # Keeps the AI focused, no creative writing
            )
            action = response.choices[0].message.content.strip()

            # The environment processes the move
            obs, reward, done = env.step(action)

            # MANDATORY: Step tag for the grader
            print(f"[STEP] step={env.step_count} action={action} reward={reward}", flush=True)

            # Add the result to memory so the AI knows what happened
            chat_history.append({"role": "assistant", "content": action})
            chat_history.append({"role": "user", "content": f"System Response: {obs}"})

        # MANDATORY: End tag with the final dynamic score!
        print(f"[END] task=Incident_Resolution score={reward} steps={env.step_count}", flush=True)

    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        # Failsafe end tag so the grader doesn't freeze
        print(f"[END] task=Incident_Resolution score=0.1 steps={env.step_count}", flush=True)

if __name__ == "__main__":
    run_agent()
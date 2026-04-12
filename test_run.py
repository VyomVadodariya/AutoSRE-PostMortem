import time
from sre_env import SREEnvironment

print("🚀 Starting V2 Local UI Test...")
env = SREEnvironment()

print("Switch to your Streamlit dashboard NOW! (localhost:8501)")
time.sleep(3)

# The test agent dynamically extracts the random malware PID!
randomized_malware = env.malware_pid

simulated_ai_moves = [
    "check_metrics",
    "list_processes",
    "restart_service nginx_web_server", # Agent tries to fix it early (Will Fail!)
    f"kill_process {randomized_malware}", # Agent finds and kills the dynamic PID
    "restart_service nginx_web_server"  # Agent successfully restores the server
]

for action in simulated_ai_moves:
    print(f"\n[AI is typing...] -> {action}")
    env.step(action)
    time.sleep(3)

print("\n✅ V2 Test Complete! Check the dashboard!")
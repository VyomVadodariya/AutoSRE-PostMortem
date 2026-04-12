import time
from sre_env import SREEnvironment

print("🚀 Starting Elite V3 Local UI Test...")
env = SREEnvironment()
time.sleep(2)

scenario = env.current_scenario
print(f"🔥 INJECTED SCENARIO: {scenario}")

# Create a dynamic test path based on what the environment randomly spawned
moves = ["check_metrics", "check_network"]

if scenario == "MALWARE_SPIKE":
    moves.extend(["list_processes", f"kill_process {env.malware_pid}", "restart_service nginx"])
elif scenario == "LOG_BLOAT":
    moves.extend(["inspect_logs", "clear_logs", "restart_service nginx"])
else: # HYBRID
    moves.extend([
        "list_processes", f"kill_process {env.malware_pid}", 
        "inspect_logs", "clear_logs", 
        "restart_service nginx"
    ])

for action in moves:
    print(f"\n[AI] -> {action}")
    env.step(action)
    time.sleep(3)

print("\n✅ Test Complete!")
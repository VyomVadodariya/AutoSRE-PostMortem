import time
from sre_env import SREEnvironment

print("🚀 Starting Local UI Test...")
env = SREEnvironment()

# Give you 3 seconds to switch to your browser!
print("Switch to your Streamlit dashboard NOW! (localhost:8501)")
time.sleep(3)

# We hardcode the exact moves the AI would make
simulated_ai_moves = [
    "check_metrics",
    "list_processes",
    "kill_process 2033", # Oops, the AI makes a mistake and kills the database
    "kill_process 9999"  # The AI finds the malware and fixes it!
]

for action in simulated_ai_moves:
    print(f"\n[AI is typing...] -> {action}")
    env.step(action)
    time.sleep(3) # Pause for 3 seconds so you can watch the UI update smoothly

print("\n✅ Test Complete! Did you see the dashboard update?")
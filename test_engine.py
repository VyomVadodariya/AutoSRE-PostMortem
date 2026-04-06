from environment import SREEnvironment
from models import SREAction

print("--- ⚙️ BOOTING AUTO-SRE ENGINE ---")
env = SREEnvironment()

# 1. Reset the environment (This triggers generate_logs.py in the background)
print("\n[1] Resetting Environment...")
obs = env.reset()
print(f"📍 Current Directory: {obs.current_directory}")
print(f"❤️ Initial Health: {obs.system_health_score}")

# 2. Create a mock AI action
print("\n[2] AI Agent Action: Running 'ls -la logs/'...")
test_action = SREAction(
    action_type="bash_command",
    command="ls -la logs/"
)

# 3. Step the environment and capture the result
result = env.step(test_action)

print("\n[3] Environment Terminal Output:")
print("-" * 40)
print(result.observation.terminal_output)
print("-" * 40)
print(f"❤️ New Health Score: {result.observation.system_health_score}")
print(f"💰 Reward Given: {result.reward}")
print(f"🏁 Episode Done: {result.done}")
print("--- ✅ TEST COMPLETE ---")
import requests

# Your live cloud API endpoints
BASE_URL = "https://vyomvadodariya-autosre-postmortem-v1.hf.space"
STEP_URL = f"{BASE_URL}/step"

print("🤖 [AI AGENT] Connecting to AutoSRE Cloud Environment...")

# 1. The AI decides to take an action
ai_action = {"command": "block ip 192.168.1.50"}
print(f"🤖 [AI AGENT] Executing command: '{ai_action['command']}'")

try:
    # 2. We send the action to your Consequence Engine in the cloud
    response = requests.post(STEP_URL, json=ai_action)
    
    if response.status_code == 200:
        result = response.json()
        print("\n🌍 [CLOUD ENVIRONMENT RESPONSE]")
        print(f"👁️  Observation: {result['observation']}")
        print(f"🏆 Reward:      {result['reward']}")
        print(f"🏁 Is Done?:    {result['done']}")
    else:
        print(f"❌ ERROR: Server returned {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"🚨 CONNECTION FAILED: {e}")
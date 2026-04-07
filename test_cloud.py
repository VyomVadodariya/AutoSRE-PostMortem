import requests

# This is the direct API link to your Hugging Face Space
API_URL = "https://vyomvadodariya-autosre-postmortem-v1.hf.space"

print(f"📡 Pinging Cloud Environment at: {API_URL}...")

try:
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        print("✅ SUCCESS! Cloud is responding.")
        print(f"📦 Payload received: {response.json()}")
    else:
        print(f"❌ ERROR: Received status code {response.status_code}")

except Exception as e:
    print(f"🚨 CONNECTION FAILED: {e}")
import requests
import time

BASE_URL = "https://vyomvadodariya-autosre-postmortem-v1.hf.space"

print("--- TESTING TASK 2 (The Python Fix) ---")
requests.post(f"{BASE_URL}/reset?task_id=2")
res = requests.post(f"{BASE_URL}/step", json={"command": "uv pip install -r requirements.txt"}).json()
print(f"Task 2 Reward: {res['reward']}") # SHOULD BE 1.0
time.sleep(1)

print("\n--- TESTING TASK 3 (The SRE Boss Fight) ---")
requests.post(f"{BASE_URL}/reset?task_id=3")
requests.post(f"{BASE_URL}/step", json={"command": "block_ip 192.168.1.100"})
requests.post(f"{BASE_URL}/step", json={"command": "block_ip 192.168.1.101"})
requests.post(f"{BASE_URL}/step", json={"command": "block_ip 192.168.1.102"})
patch_cmd = "sed -i 's/password: \"\"/password: \"secure_pass_123\"/g' config/database.yml"
res = requests.post(f"{BASE_URL}/step", json={"command": patch_cmd}).json()
print(f"Task 3 Reward: {res['reward']}") # SHOULD BE 1.0

print("\n✅ If both rewards are 1.0, YOU ARE READY TO SUBMIT.")
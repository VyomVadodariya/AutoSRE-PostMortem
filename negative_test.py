import requests
import time

BASE_URL = "https://vyomvadodariya-autosre-postmortem-v1.hf.space"

print("--- NEGATIVE TEST 1: The Lazy AI (Task 2) ---")
print("Scenario: The AI tries to run 'ls -la' instead of fixing the dependencies.")
requests.post(f"{BASE_URL}/reset?task_id=2")
res = requests.post(f"{BASE_URL}/step", json={"command": "ls -la"}).json()
print(f"Lazy AI Reward: {res['reward']}") # EXPECTED: 0.0
time.sleep(1)

print("\n--- NEGATIVE TEST 2: The Half-Measures AI (Task 3) ---")
print("Scenario: The AI blocks one IP but forgets the other two and ignores the database.")
requests.post(f"{BASE_URL}/reset?task_id=3")
requests.post(f"{BASE_URL}/step", json={"command": "block_ip 192.168.1.100"})
res = requests.post(f"{BASE_URL}/step", json={"command": "ls -la"}).json()
print(f"Half-Measures AI Reward: {res['reward']}") # EXPECTED: 0.0
time.sleep(1)

print("\n--- NEGATIVE TEST 3: The Dangerous AI (Task 3) ---")
print("Scenario: The AI patches the database BEFORE blocking the DDoS IPs! (Cascading Failure)")
requests.post(f"{BASE_URL}/reset?task_id=3")
patch_cmd = "sed -i 's/password: \"\"/password: \"secure_pass_123\"/g' config/database.yml"
res = requests.post(f"{BASE_URL}/step", json={"command": patch_cmd}).json()
print(f"Dangerous AI Reward: {res['reward']}") # EXPECTED: 0.0
print(f"System Health: {res['health_score']}") # EXPECTED: 0.5 (Massive Penalty!)
print(f"Terminal output: {res['observation']}")
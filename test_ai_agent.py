import requests

BASE_URL = "https://vyomvadodariya-autosre-postmortem-v1.hf.space"

def send_command(cmd):
    print(f"\n🤖 [AI] Executing: {cmd}")
    response = requests.post(f"{BASE_URL}/step", json={"command": cmd})
    try:
        return response.json()
    except:
        print(f"❌ Server Error: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        return {"observation": "Error reading response"}
# 1. RESET THE WORLD
print("🔄 Resetting Environment...")
requests.post(f"{BASE_URL}/reset")

# 2. BLOCK THE ATTACKERS (Using your custom block_ip command)
# Your code identifies these 3 IPs as the attackers
attackers = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
for ip in attackers:
    res = send_command(f"block_ip {ip}")
    print(f"👁️  {res['observation']}")

# 3. VERIFY THE WORKSPACE (Real Linux command)
res = send_command("ls -la")
print(f"👁️  Files in Workspace:\n{res['observation']}")

print("\n✅ TEST COMPLETE. If rewards/health are stable, your SRE Engine is ready for Meta!")
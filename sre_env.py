import json
import time
import random

class SREEnvironment:
    def __init__(self):
        self.reset()

    def reset(self):
        """Resets the server with dynamic, randomized issues."""
        # The malware hides under a new PID every single time!
        self.malware_pid = str(random.randint(7000, 9999)) 
        
        self.state = {
            "cpu_usage": 99.9,
            "system_health": "CRITICAL",
            "services": {
                "nginx_web_server": "OFFLINE",
                "mysql_database": "ONLINE"
            },
            "active_processes": {
                "1042": "nginx_worker", 
                "2033": "mysql_daemon", 
                self.malware_pid: "kdevtmpfsi" # The hidden malware
            }
        }
        self.step_count = 0
        self.max_steps = 10
        self.malware_killed = False
        self.update_telemetry("Environment V2 Initialized. Dynamic generation active.", 0)
        return "ALERT: CPU Critical. Nginx is OFFLINE. Investigate and restore services."

    def update_telemetry(self, last_output, reward):
        ui_state = {
            "system_health_score": reward,
            "step_count": self.step_count,
            "last_reward": reward,
            "current_task": "Multi-Step Incident Remediation",
            "last_action_output": last_output,
            "workspace_state": self.state
        }
        try:
            with open("observation.json", "w") as f:
                json.dump(ui_state, f)
        except:
            pass

    def step(self, action):
        self.step_count += 1
        reward = 0.0
        done = False
        observation = ""
        action = action.strip().lower()

        if action == "check_metrics":
            observation = f"CPU: {self.state['cpu_usage']}%. Services: {self.state['services']}"
            reward = -0.1 
            
        elif action == "list_processes":
            observation = f"Running PIDs: {list(self.state['active_processes'].keys())} - Names: {list(self.state['active_processes'].values())}"
            reward = -0.1

        elif action.startswith("kill_process"):
            parts = action.split()
            if len(parts) == 2:
                pid = parts[1]
                if pid == self.malware_pid:
                    self.state["cpu_usage"] = 15.0
                    self.malware_killed = True
                    del self.state["active_processes"][pid]
                    observation = f"SUCCESS: Process {pid} terminated. CPU stabilized. However, Nginx is still OFFLINE."
                    reward = 0.5 # Half points for neutralizing the threat
                elif pid in self.state["active_processes"]:
                    observation = f"CRITICAL ERROR: You killed {self.state['active_processes'][pid]}! System unstable."
                    reward = -0.8
                else:
                    observation = f"ERROR: PID {pid} not found."
                    reward = -0.1
            else:
                observation = "ERROR: Use format 'kill_process <pid>'"
                reward = -0.1

        # THE NEW FIX ACTION
        elif action.startswith("restart_service"):
            parts = action.split()
            if len(parts) == 2:
                service = parts[1]
                if service == "nginx_web_server":
                    if self.malware_killed:
                        self.state["services"]["nginx_web_server"] = "ONLINE"
                        self.state["system_health"] = "STABLE"
                        observation = "SUCCESS: Nginx restarted safely. System fully restored!"
                        reward = 1.0 # Full points for actually fixing it!
                        done = True
                    else:
                        observation = "ERROR: Nginx failed to start. CPU is too high. You must kill the rogue process first."
                        reward = -0.3
                else:
                    observation = f"ERROR: Service '{service}' not recognized."
                    reward = -0.1
            else:
                observation = "ERROR: Use format 'restart_service <name>'"
                reward = -0.1
        else:
            observation = f"ERROR: Unknown command. Allowed: [check_metrics, list_processes, kill_process <pid>, restart_service <name>]"
            reward = -0.1

        if self.step_count >= self.max_steps and not done:
            done = True
            observation += " | CRITICAL FAILURE: Maximum steps reached. Server crashed."
            reward = -1.0
            self.state["system_health"] = "OFFLINE"

        self.update_telemetry(f"> {action}\n{observation}", reward)
        time.sleep(1.5) 

        return observation, reward, done
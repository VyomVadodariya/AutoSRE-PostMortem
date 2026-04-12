import json
import time

class SREEnvironment:
    def __init__(self):
        # We start by forcing a reset to get the initial broken state
        self.reset()

    def reset(self):
        """Resets the server to its initial broken state."""
        self.state = {
            "cpu_usage": 99.9,
            "memory_usage": "85%",
            "active_processes": {
                "1042": "nginx", 
                "2033": "mysql", 
                "9999": "kdevtmpfsi" # Classic crypto-miner malware name
            },
            "system_health": "CRITICAL"
        }
        self.step_count = 0
        self.max_steps = 7
        self.update_telemetry("Environment Initialized. Awaiting AI connection...", 0)
        return "ALERT: CPU Usage Critical at 99.9%. Investigate immediately."

    def update_telemetry(self, last_output, reward):
        """Secretly updates your Streamlit dashboard after every move!"""
        ui_state = {
            "system_health_score": reward,
            "step_count": self.step_count,
            "last_reward": reward,
            "current_task": "Interactive Debugging Session",
            "last_action_output": last_output,
            "workspace_state": self.state
        }
        try:
            with open("observation.json", "w") as f:
                json.dump(ui_state, f)
        except:
            pass

    def step(self, action):
        """The core OpenEnv game loop. Takes an AI action, returns (obs, reward, done)."""
        self.step_count += 1
        reward = 0.0
        done = False
        observation = ""

        # Clean the AI's input
        action = action.strip().lower()

        # ACTION 1: Check Metrics
        if action == "check_metrics":
            observation = f"CPU: {self.state['cpu_usage']}%, Memory: {self.state['memory_usage']}"
            reward = -0.1 # Slight time penalty for gathering info
            
        # ACTION 2: List Processes
        elif action == "list_processes":
            observation = f"Running PIDs: {list(self.state['active_processes'].keys())} - Names: {list(self.state['active_processes'].values())}"
            reward = -0.1

        # ACTION 3: Kill a Process
        elif action.startswith("kill_process"):
            parts = action.split()
            if len(parts) == 2:
                pid = parts[1]
                if pid == "9999":
                    # SUCCESS! The AI found the malware.
                    self.state["cpu_usage"] = 12.0
                    self.state["system_health"] = "STABLE"
                    del self.state["active_processes"][pid]
                    observation = f"SUCCESS: Process {pid} terminated. CPU dropped to 12%. System restored."
                    reward = 1.0 # Max points!
                    done = True
                elif pid in self.state["active_processes"]:
                    # AI killed a good process
                    observation = f"ERROR: Killed {pid} ({self.state['active_processes'][pid]}), but CPU is still high. You broke a vital service."
                    reward = -0.5
                else:
                    observation = f"ERROR: PID {pid} not found."
                    reward = -0.2
            else:
                observation = "ERROR: Invalid command format. Use 'kill_process <pid>'"
                reward = -0.2
        else:
            observation = f"ERROR: Unknown command '{action}'. Available commands: [check_metrics, list_processes, kill_process <pid>]"
            reward = -0.2

        # Check for timeout
        if self.step_count >= self.max_steps and not done:
            done = True
            observation += " | CRITICAL FAILURE: Maximum steps reached. Server crashed."
            reward = -1.0
            self.state["system_health"] = "OFFLINE"

        # Push updates to the UI
        self.update_telemetry(f"> {action}\n{observation}", reward)
        
        # Pause briefly so the UI update looks cool and natural
        time.sleep(1.5) 

        return observation, reward, done
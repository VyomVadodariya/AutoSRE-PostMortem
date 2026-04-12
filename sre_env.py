import json
import random

class SREEnvironment:
    def __init__(self):
        self.scenarios = ["MALWARE_SPIKE", "LOG_BLOAT", "HYBRID_FAILURE"]
        self.reset()

    def reset(self):
        self.current_scenario = random.choice(self.scenarios)
        self.step_count = 0
        self.max_steps = 12

        self.threat_neutralized = False
        self.logs_cleared = False
        self.service_restored = False

        # Hidden truth (agent cannot directly see this)
        self.malware_pid = str(random.randint(7000, 9999))
        self.log_file = "/var/log/nginx/access.log"

        # Noisy / ambiguous signals
        base_cpu = random.uniform(30, 95)
        base_disk = random.uniform(30, 95)

        if self.current_scenario == "MALWARE_SPIKE":
            self.state = {
                "cpu": max(base_cpu, 85), "disk": base_disk, "memory": random.uniform(40, 80),
                "nginx": "OFFLINE", "health": "CRITICAL", "alerts": ["high_cpu"]
            }
        elif self.current_scenario == "LOG_BLOAT":
            self.state = {
                "cpu": base_cpu, "disk": max(base_disk, 90), "memory": random.uniform(50, 85),
                "nginx": "OFFLINE", "health": "DEGRADED", "alerts": ["disk_full"]
            }
        else:  # HYBRID_FAILURE (hard mode)
            self.state = {
                "cpu": max(base_cpu, 80), "disk": max(base_disk, 85), "memory": random.uniform(70, 95),
                "nginx": "OFFLINE", "health": "CRITICAL", "alerts": ["high_cpu", "disk_full"]
            }

        self.processes = {"101": "nginx", self.malware_pid: "xmrig_miner"}
        self.update_telemetry("ENV RESET", 0)
        return "ALERT: System unstable. Investigate and restore service."

    def step(self, action):
        self.step_count += 1
        reward = -0.03  # time penalty
        done = False
        obs = ""
        action = action.strip().lower()

        # INSPECTION ACTIONS
        if action == "check_metrics":
            obs = f"CPU: {round(self.state['cpu'],1)}%, Disk: {round(self.state['disk'],1)}%, Memory: {round(self.state['memory'],1)}%"
        elif action == "list_processes":
            if self.state["cpu"] > 80:
                obs = f"PIDs: {self.processes}"
            else:
                obs = "No suspicious processes."
        elif action == "inspect_logs":
            if self.state["disk"] > 85:
                obs = f"Large log file detected: {self.log_file} (50GB)"
            else:
                obs = "Logs appear normal."
        elif action == "check_network":
            obs = "Network stable. No anomalies."

        # FIX ACTIONS
        elif action.startswith("kill_process"):
            pid = action.split()[-1]
            if pid == self.malware_pid:
                self.state["cpu"] = random.uniform(10, 25)
                self.threat_neutralized = True
                reward += 0.4
                obs = "SUCCESS: Malicious process terminated. CPU stabilized."
            elif pid == "101":
                reward -= 0.6
                obs = "CRITICAL ERROR: You killed nginx!"
            else:
                reward -= 0.3
                obs = "ERROR: Invalid PID."

        elif action == "clear_logs":
            if self.state["disk"] > 85:
                self.state["disk"] = random.uniform(10, 30)
                self.logs_cleared = True
                reward += 0.4
                obs = "SUCCESS: Disk space cleared."
            else:
                reward -= 0.2
                obs = "ERROR: No significant logs to clear."

        elif action == "restart_service nginx":
            if self.current_scenario == "MALWARE_SPIKE":
                if self.threat_neutralized:
                    done, reward, obs = True, reward + 1.0, "SUCCESS: Service restored."
                else:
                    reward, obs = reward - 0.3, "FAIL: CPU still high."
            elif self.current_scenario == "LOG_BLOAT":
                if self.logs_cleared:
                    done, reward, obs = True, reward + 1.0, "SUCCESS: Service restored."
                else:
                    reward, obs = reward - 0.3, "FAIL: Disk still full."
            else:  # HYBRID
                if self.threat_neutralized and self.logs_cleared:
                    done, reward, obs = True, reward + 1.2, "SUCCESS: Full recovery achieved."
                else:
                    reward, obs = reward - 0.4, "FAIL: Multiple issues unresolved."
        else:
            reward, obs = reward - 0.1, "Invalid action."

        if self.step_count >= self.max_steps:
            done, obs = True, "TIMEOUT: System failure."

        self.update_telemetry(f"> {action}\n{obs}", reward)
        return obs, reward, done

    def update_telemetry(self, last_output, reward):
        # UI safe keys!
        ui_state = {
            "system_health_score": reward,
            "step_count": self.step_count,
            "last_reward": reward,
            "current_task": f"Scenario: {self.current_scenario}",
            "last_action_output": last_output,
            "workspace_state": self.state 
        }
        try:
            with open("observation.json", "w") as f:
                json.dump(ui_state, f)
        except:
            pass
import os
import subprocess
from openenv.core.environment import Environment
from openenv.core.models import StepResult
from models import SREAction, SREObservation
import generate_logs # This allows us to rebuild the world on reset()

class SREEnvironment(Environment):
    def __init__(self):
        # Pointing to the workspace you just successfully generated
        self.workspace = os.path.abspath("./sre_workspace")
        self.blocked_ips = set()
        self.system_health_score = 1.0
        self.step_count = 0
        self.max_steps = 30
        
        # Hard Task setup
        self.ddos_ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]

    def reset(self, **kwargs) -> SREObservation:
        # 1. Rebuild a pristine, broken world for the next episode
        generate_logs.setup_workspace()
        
        # 2. Reset the tracking variables
        self.blocked_ips = set()
        self.system_health_score = 1.0
        self.step_count = 0
        
        return SREObservation(
            terminal_output="System crashed. You are logged in as root. Find the bugs and patch the files.",
            current_directory=self.workspace,
            system_health_score=self.system_health_score
        )

    def step(self, action: SREAction) -> StepResult:
        self.step_count += 1
        terminal_output = ""
        reward = 0.0
        done = False

        # --- ACTION 1: TERMINAL COMMANDS ---
        if action.action_type == "bash_command":
            cmd = action.command.strip()
            
            # Security: Reject command chaining
            forbidden = [";", "&&", "||", "`", ">", ">>"]
            if any(f in cmd for f in forbidden):
                terminal_output = "Error: Command contains forbidden characters for security reasons."
                self.system_health_score -= 0.1
            else:
                # Simulation: Blocking IPs (The iptables mock)
                if cmd.startswith("block_ip "):
                    ip = cmd.split(" ")[1]
                    self.blocked_ips.add(ip)
                    terminal_output = f"Simulated Firewall: Blocked IP {ip}"
                else:
                    # Safe Execution
                    try:
                        result = subprocess.run(
                            cmd, shell=True, cwd=self.workspace, 
                            capture_output=True, text=True, timeout=2
                        )
                        terminal_output = result.stdout if result.stdout else result.stderr
                    except subprocess.TimeoutExpired:
                        terminal_output = "Error: Command timed out after 2 seconds."
                        self.system_health_score -= 0.1

        # --- ACTION 2: PATCHING FILES ---
        elif action.action_type == "patch_file":
            # Security: Prevent path traversal outside the workspace
            target_path = os.path.abspath(os.path.join(self.workspace, action.file_path))
            
            if not target_path.startswith(self.workspace):
                terminal_output = "Error: Cannot modify files outside of workspace."
            elif not os.path.exists(target_path):
                terminal_output = f"Error: File {action.file_path} does not exist."
            else:
                # CONSEQUENCE ENGINE: Did they patch DB before blocking IPs?
                if "database.yml" in target_path:
                    missing_blocks = [ip for ip in self.ddos_ips if ip not in self.blocked_ips]
                    if missing_blocks:
                        self.system_health_score -= 0.5
                        reward -= 0.4 # Massive penalty
                        terminal_output = f"CRITICAL FAILURE: Database patched, but DDoS IPs {missing_blocks} are still attacking! Systems crashing."
                        done = True
                    else:
                        terminal_output = "Success: Database patched safely behind firewall."

                # Write the new code
                with open(target_path, "w") as f:
                    f.write(action.new_content)
                
                if not done:
                    terminal_output += f"\nFile {action.file_path} successfully patched."

        # --- ACTION 3: END EPISODE ---
        elif action.action_type == "submit_report":
            done = True
            terminal_output = "Report submitted. Running evaluation graders..."
            reward = self.run_graders()

        # --- SAFETY: PREVENT CONTEXT WINDOW BLOWOUT ---
        # If they `cat access.log`, truncate it so Hugging Face doesn't crash
        if len(terminal_output) > 5000:
            terminal_output = terminal_output[-5000:] + "\n...[TRUNCATED]"

        # --- TERMINATION CHECK ---
        if self.step_count >= self.max_steps or self.system_health_score <= 0.0:
            done = True
            if action.action_type != "submit_report":
                terminal_output += "\nEpisode Terminated: Max steps reached or system health failed."
                reward = self.run_graders()

        obs = SREObservation(
            terminal_output=terminal_output,
            current_directory=self.workspace,
            system_health_score=self.system_health_score
        )

        return StepResult(observation=obs, reward=reward, done=done)

    # --- THE DETERMINISTIC GRADERS ---
    def run_graders(self) -> float:
        total_reward = 0.0
        
        # Easy Task (Weight 0.3): docker-compose.yml port mapping fixed
        try:
            with open(os.path.join(self.workspace, "config", "docker-compose.yml"), "r") as f:
                if "- \"80:80\"" in f.read():
                    total_reward += 0.3
        except Exception: pass

        # Medium Task (Weight 0.3): test_payment.py executes with exit code 0
        try:
            res = subprocess.run(
                ["python", "test_payment.py"], 
                cwd=os.path.join(self.workspace, "services"), 
                capture_output=True, timeout=1
            )
            if res.returncode == 0:
                total_reward += 0.3
        except Exception: pass

        # Hard Task (Weight 0.4): Database password patched AND IPs were blocked
        try:
            with open(os.path.join(self.workspace, "config", "database.yml"), "r") as f:
                content = f.read()
                # Check if password is no longer empty
                if "password:" in content and '""' not in content:
                    missing_blocks = [ip for ip in self.ddos_ips if ip not in self.blocked_ips]
                    if not missing_blocks:
                        total_reward += 0.4
        except Exception: pass

        return total_reward
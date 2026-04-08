import os
import subprocess
from openenv.core.environment import Environment
from openenv.core.models import StepResult
from models import SREAction, SREObservation
import generate_logs

class SREEnvironment(Environment):
    def __init__(self):
        self.workspace = os.path.abspath("./sre_workspace")
        self.blocked_ips = set()
        self.system_health_score = 1.0
        self.step_count = 0
        self.max_steps = 30
        self.current_task = "3"
        self.ddos_ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]

    def reset(self, task_id="3", **kwargs) -> SREObservation:
        self.current_task = task_id
        generate_logs.setup_workspace()
        
        self.blocked_ips = set()
        self.system_health_score = 1.0
        self.step_count = 0
        
        if self.current_task == "1":
            obs_text = "System crashed. Docker configuration is invalid. Fix the port mappings."
        elif self.current_task == "2":
            obs_text = "System crashed. Dependencies missing. Fix the Python environment."
        else:
            obs_text = "System crashed. You are logged in as root. Find the bugs and patch the files."

        return SREObservation(
            terminal_output=obs_text,
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
                    try:
                        ip = cmd.split(" ")[1]
                        self.blocked_ips.add(ip)
                        terminal_output = f"Simulated Firewall: Blocked IP {ip}"
                    except IndexError:
                        terminal_output = "Error: Invalid syntax. Use 'block_ip <IP>'"
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
            target_path = os.path.abspath(os.path.join(self.workspace, action.file_path))
            
            if not target_path.startswith(self.workspace):
                terminal_output = "Error: Cannot modify files outside of workspace."
            elif not os.path.exists(target_path):
                terminal_output = f"Error: File {action.file_path} does not exist."
            else:
                if "database.yml" in target_path:
                    missing_blocks = [ip for ip in self.ddos_ips if ip not in self.blocked_ips]
                    if missing_blocks:
                        self.system_health_score -= 0.5
                        terminal_output = f"CRITICAL FAILURE: Database patched, but DDoS IPs {missing_blocks} are still attacking! Systems crashing."
                        done = True
                    else:
                        terminal_output = "Success: Database patched safely behind firewall."

                with open(target_path, "w") as f:
                    f.write(action.new_content)
                
                if not done:
                    terminal_output += f"\nFile {action.file_path} successfully patched."

        # --- SAFETY: PREVENT CONTEXT WINDOW BLOWOUT ---
        if len(terminal_output) > 5000:
            terminal_output = terminal_output[-5000:] + "\n...[TRUNCATED]"

        # --- DENSE REWARD ROUTING ---
        if self.current_task == "1":
            reward = self.grade_task_1()
        elif self.current_task == "2":
            cmd_text = action.command if action.action_type == "bash_command" else ""
            reward = self.grade_task_2(cmd_text)
        elif self.current_task == "3":
            reward = self.grade_task_3()

        if reward >= 1.0:
            done = True
            terminal_output += f"\n✅ [SUCCESS] Task {self.current_task} Objective Completed!"

        if self.step_count >= self.max_steps or self.system_health_score <= 0.0:
            done = True
            if self.system_health_score <= 0.0:
                terminal_output += "\nEpisode Terminated: System health failed."

        obs = SREObservation(
            terminal_output=terminal_output,
            current_directory=self.workspace,
            system_health_score=self.system_health_score
        )

        return StepResult(observation=obs, reward=reward, done=done)

    # --- THE ISOLATED TASK GRADERS ---
    def grade_task_1(self) -> float:
        try:
            with open(os.path.join(self.workspace, "config", "docker-compose.yml"), "r") as f:
                if "- \"80:80\"" in f.read():
                    print("✅ [SUCCESS] Task 1 cleared with reward 1.0!")
                    return 1.0
        except Exception: pass
        return 0.0

    def grade_task_2(self, cmd: str) -> float:
        if "pip install" in cmd or "uv pip install" in cmd or "uv sync" in cmd:
            print("✅ [SUCCESS] Task 2 cleared with reward 1.0!")
            return 1.0
        return 0.0

    def grade_task_3(self) -> float:
        try:
            with open(os.path.join(self.workspace, "config", "database.yml"), "r") as f:
                content = f.read()
                if "password:" in content and '""' not in content:
                    missing_blocks = [ip for ip in self.ddos_ips if ip not in self.blocked_ips]
                    if not missing_blocks:
                        print("✅ [SUCCESS] Task 3 cleared with reward 1.0!")
                        return 1.0
        except Exception: pass
        return 0.0
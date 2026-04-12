# 🚨 AutoSRE: Autonomous Incident Recovery Environment

**A Reinforcement Learning simulation for training AI to autonomously debug and resolve production server outages.** Built for the Meta PyTorch OpenEnv Hackathon.

### ⏱️ The 10-Second Pitch
Most AI SRE tools just *read logs* and write post-mortems. **AutoSRE is a live, interactive game board.** We built a Reinforcement Learning environment that simulates a critical production server crash (a crypto-miner maxing out CPU). An autonomous AI agent connects to this environment, strictly uses system commands to investigate, and terminates the malware—all visualized on a real-time, dark-mode telemetry dashboard.

---

## 🏗️ The Architecture (OpenEnv Compliant)

We pivoted from a static LLM prompt script to a fully interactive State/Action/Reward environment. AutoSRE is divided into three distinct layers:

* 🎮 **The Game Board (`sre_env.py`)**: The simulation. It maintains the server state, accepts strictly formatted actions, dynamically calculates rewards (+1 for fixing the server, -0.5 for crashing a database), and outputs observations.
* 🤖 **The Player (`inference.py`)**: The autonomous agent. It connects via proxy, reads the environment's state, and loops through a strict action space (`check_metrics`, `list_processes`, `kill_process`) until the root cause is resolved.
* 📊 **The Spectator (`dashboard.py`)**: A real-time Streamlit UI. The environment silently dumps state changes to `observation.json`, rendering a live command-center view of the AI's debugging process.

---

## 🚀 Quick Start Guide

Want to watch the AI battle the server outage in real-time? You can run the entire simulation locally.

**1. Start the Live Telemetry UI:**
Open a terminal, activate your virtual environment, and boot the Streamlit dashboard.
```bash
streamlit run dashboard.py
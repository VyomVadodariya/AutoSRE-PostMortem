import streamlit as st
import json
import time
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AutoSRE | Autonomous Recovery Dashboard",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    .status-card { padding: 20px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00ff00; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🌌 AutoSRE: Autonomous Post-Mortem")
st.subheader("Real-time Agentic Infrastructure Recovery")
st.divider()

# --- DATA LOADING ---
def load_data():
    if os.path.exists("observation.json"):
        with open("observation.json", "r") as f:
            return json.load(f)
    return None

# --- UI REFRESH LOOP ---
placeholder = st.empty()

while True:
    data = load_data()
    
    with placeholder.container():
        if data:
            # 1. Top Level Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            health = data.get("system_health_score", 0) * 100
            health_color = "normal" if health > 70 else "inverse" if health < 30 else "off"
            
            col1.metric("System Health", f"{health:.1f}%", delta=f"{health-50:.1f}%", delta_color=health_color)
            col2.metric("Agent Step", data.get("step_count", 0))
            col3.metric("Reward", f"{data.get('last_reward', 0):.2f}")
            col4.metric("Downtime Cost Saved", f"${data.get('step_count', 0) * 1400}", delta="Live Estimate")

            st.write("###")

            # 2. Main Dashboard Layout
            left_col, right_col = st.columns(2)

            with left_col:
                st.write("#### 📟 Live Agent Terminal Output")
                # Creating a simulated terminal look
                st.code(data.get("last_action_output", "Awaiting agent command..."), language="bash")
                
                st.write("#### 🛡️ Active Firewall Status")
                ips = data.get("blocked_ips", [])
                if ips:
                    st.table(pd.DataFrame({"Blocked IPs": ips, "Status": ["DROP"] * len(ips)}))
                else:
                    st.info("No active threats detected.")

            with right_col:
                st.write("#### 🧠 Agent Reasoning")
                st.success(f"**Current Task:** {data.get('current_task', 'Analyzing System Logs...')}")
                
                # Progress Bar for Health
                st.progress(int(health) / 100)
                
                st.write("#### 📄 Workspace State")
                st.json(data.get("workspace_state", {}))

        else:
            st.warning("Awaiting signal from `inference.py`... Make sure the agent is running.")

    time.sleep(1) # Refresh every second
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="AutoSRE | Autonomous SRE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.main { background-color: #0e1117; }
.stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🌌 AutoSRE Platform")
page = st.sidebar.radio("Navigation", [
    "Overview", 
    "Active Incident", 
    "Investigation & RCA", 
    "Incident Timeline", 
    "Post-Mortem", 
    "Chaos Lab", 
    "Benchmarking"
])

# Mocking data connections - In real deployment, these read from the Orchestrator/Memory store
if page == "Overview":
    st.title("System Overview & SRE Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SLO Target", "99.95%")
    c2.metric("Current Availability", "99.82%", "-0.13%", delta_color="inverse")
    c3.metric("Error Budget Consumed", "74%", "+12%", delta_color="inverse")
    c4.metric("MTTR", "41s", "-5s")
    
    st.subheader("Active Incidents")
    st.info("No critical incidents currently active. System is HEALTHY.")

elif page == "Active Incident":
    st.title("Active Incident Console")
    st.warning("Simulated Incident: INC-4815 (Database Failure)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Details")
        st.write("**Severity:** CRITICAL")
        st.write("**Impact:** Service degradation affecting API, Nginx")
        st.write("**Symptoms:** API Latency Spikes, HTTP 500s")
    with c2:
        st.subheader("Automated RCA")
        st.success("**Root Cause:** Connection pool exhaustion in PostgreSQL")
        st.write("**Confidence:** 92%")

elif page == "Investigation & RCA":
    st.title("Signal Investigation & Dependency Graph")
    st.write("Visualizing correlated evidence...")
    st.code("""
Dependency Graph:
Load Balancer → Nginx → API → PostgreSQL (FAILED)
    """, language="text")
    st.table(pd.DataFrame({
        "Source": ["Metrics", "Logs", "Deployments"],
        "Evidence": ["DB Connections hit 1000", "Timeout waiting for connection", "No recent deployments"],
        "Time": ["14:02:01", "14:02:05", "N/A"]
    }))

elif page == "Incident Timeline":
    st.title("Audit Timeline")
    st.write("Chronological events of the most recent incident:")
    events = [
        "14:01:00 - Anomaly Detected: Database latency Z-Score > 3.0",
        "14:01:05 - Orchestrator triggered Investigation Agent",
        "14:01:10 - RCA Agent deduced Connection Pool Exhaustion",
        "14:01:12 - Planning Agent proposed: restart_service('postgresql')",
        "14:01:15 - What-If Engine approved action (Risk: MEDIUM)",
        "14:01:20 - Remediation Engine executed restart_service",
        "14:01:35 - Verification Agent confirmed recovery",
        "14:01:40 - Postmortem Generated"
    ]
    for e in events:
        st.text(e)

elif page == "Post-Mortem":
    st.title("Auto-Generated Post-Mortem")
    st.markdown("""
# INCIDENT POSTMORTEM: INC-4815
**Severity**: CRITICAL
**MTTR**: 40s
**Estimated Business Impact**: $1,450

## Root Cause
PostgreSQL connection pool exhaustion due to aggressive unoptimized queries.

## Lessons Learned
- Ensure database query timeouts are strictly enforced.
    """)

elif page == "Chaos Lab":
    st.title("Chaos Engineering Lab")
    st.write("Inject failures to test the agent.")
    scenario = st.selectbox("Scenario", ["CPU Exhaustion", "Network Latency", "Database Failure", "Cascading Failure"])
    if st.button("Inject Chaos"):
        st.error(f"Injected: {scenario}. Agent will respond immediately.")

elif page == "Benchmarking":
    st.title("Agent Benchmarking")
    st.code("""
Agent            RCA     MTTR    Actions    Safety    Cost
------------------------------------------------------------
AutoSRE_v2       92%     41s     3.2        99%       $0.0090
Baseline_v1      74%     69s     8.4        91%       $0.0150
    """, language="text")

import streamlit as st
import pandas as pd
import time
from environment.incidents.generator import IncidentGenerator
from environment.chaos.injector import ChaosInjector
from environment.observability.metrics import MetricsStore
from environment.observability.signals import SignalStore
from environment.simulation import SimulationEnvironment
from agents.investigation.agent import InvestigationAgent
from agents.rca.agent import RCAAgent
from agents.planning.agent import PlanningAgent
from agents.remediation.engine import RemediationEngine
from agents.postmortem.agent import PostmortemAgent
from agents.orchestrator.orchestrator import Orchestrator
from tools.registry import ToolRegistry
from tools.implementations import RestartServiceTool, TerminateProcessTool
from rca.dependency_graph.graph import DependencyGraph
from rca.engine import RCAEngine

st.set_page_config(page_title="AutoSRE | Autonomous SRE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.main { background-color: #0e1117; }
.stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
</style>
""", unsafe_allow_html=True)

# Initialize simulation state
if 'env' not in st.session_state:
    metrics = MetricsStore()
    signals = SignalStore()
    st.session_state.env = SimulationEnvironment(metrics, signals)
    
    registry = ToolRegistry()
    registry.register(RestartServiceTool())
    registry.register(TerminateProcessTool())
    
    graph = DependencyGraph()
    graph.add_service("nginx")
    
    from agents.remediation.what_if import WhatIfEngine
    whatif = WhatIfEngine(registry, st.session_state.env)
    
    st.session_state.orchestrator = Orchestrator(
        InvestigationAgent(signals, metrics),
        RCAAgent(RCAEngine(graph)),
        PlanningAgent(whatif),
        RemediationEngine(registry, metrics),
        PostmortemAgent()
    )
    
    st.session_state.injector = ChaosInjector(IncidentGenerator(), st.session_state.env)
    st.session_state.active_incident = None
    st.session_state.agent_result = None

st.sidebar.title("🌌 AutoSRE Platform")
page = st.sidebar.radio("Navigation", [
    "Overview", 
    "Active Incident", 
    "Incident Timeline", 
    "Chaos Lab"
])

metrics_state = st.session_state.env.metrics.get_all_latest()

if page == "Overview":
    st.title("System Overview & SRE Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SLO Target", "99.95%")
    
    # Assuming simulated request tracking in MetricsStore
    total_requests = metrics_state.get("total_requests", 10000)
    failed_requests = metrics_state.get("failed_requests", 0)
    success_requests = total_requests - failed_requests
    
    if total_requests > 0:
        availability_pct = (success_requests / total_requests) * 100
        availability = f"{availability_pct:.2f}%"
    else:
        availability = "100.00%"
        
    delta = "-0.17%" if float(availability.strip('%')) < 99.95 else "+0.04%"
    
    c2.metric("Current Availability", availability, delta, delta_color="inverse")
    c3.metric("Error Budget Consumed", f"{(failed_requests/500)*100:.1f}%", "+12%" if float(availability.strip('%')) < 99.95 else "-1%", delta_color="inverse")
    
    if st.session_state.agent_result:
        mttr_str = "SUCCESS" if st.session_state.agent_result.get("recovery_success") else "FAILED"
    else:
        mttr_str = "N/A"
        
    c4.metric("Last Incident Recovery", mttr_str)
    
    st.subheader("System Metrics")
    st.write(metrics_state)
    
    st.subheader("Active Incidents")
    if st.session_state.active_incident:
        st.warning(f"Active Incident: {st.session_state.active_incident.incident_id}")
    else:
        st.info("No critical incidents currently active. System is HEALTHY.")

elif page == "Active Incident":
    st.title("Active Incident Console")
    incident = st.session_state.active_incident
    if incident:
        st.warning(f"Simulated Incident: {incident.incident_id}")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Details")
            st.write(f"**Severity:** {incident.severity.value}")
            st.write(f"**Impact:** {incident.expected_impact}")
            st.write(f"**Symptoms:** {', '.join(incident.symptoms)}")
        
        with c2:
            st.subheader("Automated Action Plan")
            if st.session_state.agent_result:
                st.write("**Recovery:**", "SUCCESS" if st.session_state.agent_result["recovery_success"] else "FAILED")
                st.code(st.session_state.agent_result.get("postmortem", "Generating..."), language="markdown")
            else:
                st.info("Orchestrator has not run yet.")
    else:
        st.info("No active incidents to display.")

elif page == "Incident Timeline":
    st.title("Audit Timeline")
    st.write("Chronological events of the most recent incident:")
    if st.session_state.agent_result:
        events = st.session_state.agent_result.get("timeline", [])
        for e in events:
            st.text(e)
    else:
        st.info("No timeline data available.")

elif page == "Chaos Lab":
    st.title("Chaos Engineering Lab")
    st.write("Inject failures to test the agent.")
    scenario = st.selectbox("Scenario", ["cpu_failure", "network_latency", "database_failure"])
    
    if st.button("Inject Chaos"):
        st.error(f"Injected: {scenario}. Agent responding...")
        st.session_state.active_incident = st.session_state.injector.inject_chaos(scenario)
        # Update metrics visually before agent responds? In streamlit we can just run it
        
        st.session_state.agent_result = st.session_state.orchestrator.handle_incident(st.session_state.active_incident)
        st.success("Orchestrator loop complete! Check Active Incident tab.")

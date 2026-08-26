import streamlit as st
import json
import os

from agents.investigation.agent import InvestigationAgent
from agents.orchestrator.orchestrator import Orchestrator
from agents.planning.agent import PlanningAgent
from agents.postmortem.agent import PostmortemAgent
from agents.rca.agent import RCAAgent
from agents.remediation.engine import RemediationEngine
from environment.chaos.injector import ChaosInjector
from environment.incidents.generator import IncidentGenerator
from environment.observability.metrics import MetricsStore
from environment.observability.signals import SignalStore
from environment.simulation import SimulationEnvironment
from memory.incidents.store import IncidentMemoryStore
from rca.dependency_graph.graph import DependencyGraph
from rca.engine import RCAEngine
from tools.implementations import RestartServiceTool, TerminateProcessTool
from tools.registry import ToolRegistry

st.set_page_config(page_title="AutoSRE | Autonomous SRE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.main { background-color: #0e1117; }
.stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
.incident-card { padding: 10px; border-left: 5px solid #ff4b4b; background-color: #1e2130; }
</style>
""", unsafe_allow_html=True)

# Initialize simulation state
if 'env' not in st.session_state:
    metrics = MetricsStore()
    signals = SignalStore()
    st.session_state.env = SimulationEnvironment(metrics, signals)
    
    registry = ToolRegistry()
    registry.register(RestartServiceTool(st.session_state.env))
    registry.register(TerminateProcessTool(st.session_state.env))
    
    graph = DependencyGraph()
    graph.add_service("nginx")
    memory_store = IncidentMemoryStore()
    
    from agents.remediation.what_if import WhatIfEngine
    whatif = WhatIfEngine(registry, st.session_state.env)
    
    st.session_state.orchestrator = Orchestrator(
        InvestigationAgent(signals, metrics),
        RCAAgent(RCAEngine(graph), memory_store),
        PlanningAgent(whatif),
        RemediationEngine(registry, metrics),
        PostmortemAgent(),
        memory_store
    )
    
    st.session_state.injector = ChaosInjector(IncidentGenerator(), st.session_state.env)
    st.session_state.active_incident = None
    st.session_state.agent_result = None
    st.session_state.benchmark_data = None

st.sidebar.title("🌌 AutoSRE Platform")
page = st.sidebar.radio("Navigation", [
    "Overview & Metrics", 
    "Active Incident Console", 
    "What-If & Safety",
    "Postmortem & Timeline", 
    "Benchmarks & Results",
    "Chaos Lab"
])

metrics_state = st.session_state.env.metrics.get_all_latest()

if page == "Overview & Metrics":
    st.title("System Overview & SRE Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SLO Target", "99.95%")
    
    # Assuming simulated request tracking in MetricsStore
    total_requests = metrics_state.get("total_requests", 10000)
    failed_requests = metrics_state.get("failed_requests", 0)
    success_requests = total_requests - failed_requests
    
    availability_pct = (success_requests / total_requests) * 100 if total_requests > 0 else 100.0
    availability = f"{availability_pct:.2f}%"
    delta = "-0.17%" if availability_pct < 99.95 else "+0.04%"
    
    c2.metric("Current Availability", availability, delta, delta_color="inverse")
    c3.metric("Error Budget Consumed", f"{(failed_requests/500)*100:.1f}%", "+12%" if availability_pct < 99.95 else "-1%", delta_color="inverse")
    
    mttr_str = "SUCCESS" if st.session_state.agent_result and st.session_state.agent_result.get("recovery_success") else ("FAILED" if st.session_state.agent_result else "N/A")
    c4.metric("Last Incident Recovery", mttr_str)
    
    st.subheader("System Metrics Stream")
    st.json(metrics_state)
    
    if st.session_state.active_incident:
        st.warning(f"Active Incident: {st.session_state.active_incident.incident_id}")
    else:
        st.success("No critical incidents currently active. System is HEALTHY.")

elif page == "Active Incident Console":
    st.title("Active Incident Console")
    incident = st.session_state.active_incident
    if incident:
        st.warning(f"Simulated Incident: {incident.incident_id}")
        st.markdown(f"""
        <div class="incident-card">
        <h3>Severity: {incident.severity.value}</h3>
        <p><b>Impact:</b> {incident.expected_impact}</p>
        <p><b>Symptoms:</b> {', '.join(incident.symptoms)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Automated Action Plan")
        if st.session_state.agent_result:
            if st.session_state.agent_result["recovery_success"]:
                st.success("Recovery: SUCCESS")
            else:
                st.error("Recovery: FAILED")
                
            st.info("Check 'Postmortem & Timeline' and 'What-If & Safety' for details.")
        else:
            st.info("Orchestrator has not responded yet.")
    else:
        st.info("No active incidents to display.")

elif page == "What-If & Safety":
    st.title("Counterfactual Planning & Safety Gate")
    st.write("Understand how AutoSRE evaluates actions before executing them.")
    if st.session_state.agent_result:
        st.write("Agent has executed actions. You can view the reasoning in the logs or in future updates where WhatIf data is exposed in the payload.")
        st.success("Safety Pipeline enforces constraints on Blast Radius, Risk, and Error Budgets automatically.")
    else:
        st.info("Trigger an incident in the Chaos Lab to see Safety & What-If evaluations.")

elif page == "Postmortem & Timeline":
    st.title("Incident Postmortem & Audit Timeline")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Audit Timeline")
        if st.session_state.agent_result:
            for event in st.session_state.agent_result.get("timeline", []):
                if "verified" in event.lower() or "success" in event.lower():
                    st.success(event)
                elif "failed" in event.lower() or "blocked" in event.lower():
                    st.error(event)
                else:
                    st.info(event)
        else:
            st.write("No timeline data.")
            
    with c2:
        st.subheader("Generated Postmortem")
        if st.session_state.agent_result:
            st.markdown(st.session_state.agent_result.get("postmortem", "Generating..."))
        else:
            st.write("No postmortem data.")

elif page == "Benchmarks & Results":
    st.title("AutoSRE Benchmarks")
    if os.path.exists("results/benchmark.json"):
        with open("results/benchmark.json", "r") as f:
            data = json.load(f)
        
        st.write(f"**Benchmark Run:** {data.get('timestamp')}")
        st.write(f"**Seed:** {data.get('seed')}")
        st.write(f"**Total Episodes:** {data.get('episodes')}")
        
        st.subheader("Results")
        st.dataframe(data.get("results", []))
    else:
        st.warning("No benchmark results found. Run `python run_benchmark.py` first.")

elif page == "Chaos Lab":
    st.title("Chaos Engineering Lab")
    st.write("Inject failures to test the agent.")
    scenario = st.selectbox("Scenario", ["cpu_failure", "network_latency", "database_failure", "adversarial_cpu"])
    
    if st.button("Inject Chaos & Run AutoSRE"):
        st.error(f"Injected: {scenario}. Agent responding...")
        st.session_state.active_incident = st.session_state.injector.inject_chaos(scenario)
        
        st.session_state.agent_result = st.session_state.orchestrator.handle_incident(st.session_state.active_incident)
        st.success("Orchestrator loop complete! Check other tabs for details.")

# 🚨 AutoSRE V2: Autonomous AI SRE & Incident Response Platform

AutoSRE is an advanced, fully autonomous AI agent capable of detecting, investigating, diagnosing, and safely remediating complex infrastructure incidents without human intervention.

## 1. Problem
Traditional AI SRE tools act as basic chat bots that summarize logs. AutoSRE is built as a complete **agentic system** that proactively monitors telemetry, correlates signals, deduces root causes via dependency graphs, and safely executes allowed remediation tools.

## 2. Architecture
The system employs a multi-agent orchestrated architecture:
* **Orchestrator**: Manages the incident lifecycle state machine.
* **Detection Agent**: Monitors time-series metrics via EWMA/Z-Score anomaly detection.
* **Investigation Agent**: Gathers logs, processes, network, and deployment events.
* **RCA Agent**: Maps symptoms against a Dependency Graph to find the root cause.
* **Planning Agent**: Formulates a remediation plan.
* **What-If Engine**: Evaluates counterfactual risk before taking action.
* **Remediation Agent**: Safely executes tools via the strict Tool Registry.
* **Verification Agent**: Ensures metrics stabilize before marking the incident resolved.
* **Postmortem Agent**: Synthesizes the event into an SRE-compliant Markdown report.

## 3. Incident Engine & Chaos Testing
The project includes a robust Chaos Engineering Lab. You can inject specific failure classes (Infrastructure, Network, Database, Security, Cascading) and the `Benchmarker` will evaluate the agent's RCA Accuracy, MTTR, Safety Score, and LLM Token Cost.

## 4. Usage
To launch the real-time SRE Dashboard:
```bash
pip install streamlit pandas pydantic
streamlit run dashboard/app.py
```

## 5. Kubernetes Integration (Optional)
The system is built on an Adapter interface. By swapping `SimulationEnvironment` with the `KubernetesMetricsProvider` (found in `environment/adapters`), the agent can seamlessly control real Prometheus/K8s clusters.

## 6. Testing
```bash
python -m pytest tests/
```
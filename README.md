# AutoSRE

## Overview

Modern production systems generate large volumes of metrics, logs, events, and alerts. During an incident, SRE teams must rapidly identify the cause, select a safe remediation, verify recovery, and document the incident.

AutoSRE explores how an AI-driven agent can automate this workflow inside a controlled simulation environment. It acts as an autonomous incident response platform that monitors telemetry, investigates anomalies using controlled tools, deduces root causes via dependency graphs, and safely executes allowed remediations.

## Why AutoSRE?

AutoSRE provides a robust testing ground for AI in operations. Rather than acting as a simple text-based chatbot, AutoSRE operates as a stateful, ReAct-driven loop. The simulated environment accurately mimics infrastructure behavior—terminating a runaway process naturally causes CPU metrics to drop and error rates to recover, allowing the AI's logic to be rigorously evaluated in a safe, closed loop.

## Key Capabilities

| Capability | Status |
|------------|--------|
| Dynamic incidents | Implemented |
| Time-series telemetry | Implemented |
| Anomaly detection | Implemented |
| Evidence-driven RCA | Implemented |
| Risk-aware remediation | Implemented |
| Remediation verification | Implemented |
| Incident memory | Experimental |
| Chaos engineering | Implemented |
| Benchmarking | Implemented |
| Kubernetes integration | Experimental |

## Architecture

```text
                 Incident Generator
                        |
                        v
                Simulation Environment
                        |
            +-----------+-----------+
            |           |           |
         Metrics      Logs      Services
            |           |           |
            +-----------+-----------+
                        |
                 Investigation Agent
                        |
                     Evidence
                        |
                   RCA Agent
                        |
                Remediation Planner
                        |
                  Risk / Policy
                        |
              Human Approval Layer
                        |
                 Remediation
                        |
                  Verification
                        |
                    Recovery
                        |
                  Postmortem
                        |
                 Incident Memory
                        |
                   Benchmarking
```

## End-to-End Incident Lifecycle

AutoSRE guides an incident through a deterministic, logic-driven lifecycle. The system is evaluated not on whether it blindly guesses a fix, but on how it reasons through evidence.

## AI Agent Architecture

The system employs a multi-agent orchestrated architecture governed by strict risk policies:
* **Orchestrator**: Manages the incident lifecycle state machine.
* **Investigation Agent**: Queries the state pool (processes, logs, networks) to extract anomalous evidence using a controlled tool budget.
* **RCA Agent**: Synthesizes evidence to isolate the probable root cause from a complex web of symptoms.
* **Planning Agent**: Extracts actionable parameters (like specific PIDs) from evidence and formulates a targeted remediation plan.
* **Postmortem Agent**: Synthesizes the timeline and telemetry into a compliant report.

## Simulation Environment

The project features a fully stateful simulator. Infrastructure state (active processes, database connections, active services) directly dictates the generated metrics. Remediations mutate this underlying state (e.g., removing a rogue process), causing metrics to naturally recover. 

## Observability

Telemetry is exposed via a dynamic `MetricsStore` and `SignalStore`. The agent does not cheat by accessing hidden ground-truth data; it relies entirely on its ability to request historical metrics and sift through simulated logs.

## Root Cause Analysis

RCA is structured via semantic evaluation rather than naive keyword matching. The agent's diagnosis must align with the correct failure category and pinpoint the correct underlying entity (such as a database pool vs. a generic network timeout).

## Remediation & Safety

Remediation is governed by a strict `ToolRegistry` and a What-If evaluation engine.
* Actions carry inherent risk levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
* `HIGH` risk actions mandate explicit approval policies.
* Remediation success is never assumed; the verification engine checks post-action telemetry against baseline health before closing an incident.

## Incident Memory

*(Experimental)* Previous incident vectors can be stored to improve future RCA accuracy. Production mode aims to support real embeddings, while the current test mode relies on deterministic mock representations.

## Chaos Engineering

The Chaos Injector can seamlessly simulate targeted failure classes: Infrastructure exhaustion, Network Latency, Database Failures, Security Incidents, and Cascading Multi-Service Failures. 

## Benchmarking

Benchmark results are generated from repeated incident simulations across multiple scenarios. Results should be regenerated using the benchmark suite rather than hard-coded into the documentation. 

To execute the benchmark tests (using `pytest` as the current automated runner):
```bash
pytest tests/test_benchmarker.py
```

## Example Incident

```text
Incident:
Crypto-mining process injected.

Detection:
CPU anomaly detected (97%).

Investigation:
Agent runs `get_metric_history()` and `list_processes()`.
Discovers Process 'xmrig' (PID 8472) consumes 84% CPU.

RCA:
Suspicious process is the probable root cause.

Plan:
Terminate process 8472.

Risk:
HIGH — approval required.

Execution:
Process terminated.

Verification:
CPU recovered from 97% to 19%.

Result:
Incident resolved.

Postmortem:
Generated automatically.
```

## Dashboard

The project includes a live Streamlit dashboard that binds directly to the running `SimulationEnvironment`. 

When chaos is injected from the UI, the dashboard dynamically surfaces the Orchestrator's internal thought traces, active remediation plans, and live shifts in the metric graphs. 

## Project Structure
* `agents/`: Core AI agent loops (Investigation, Planning, RCA, Postmortem)
* `dashboard/`: Streamlit interactive UI
* `environment/`: Stateful simulator, chaos injector, incident generator, and metric storage
* `evaluation/`: Benchmarker suite
* `tools/`: Tool registry and strict execution policies
* `tests/`: Automated test suite for all modules

## Installation

```bash
pip install -r requirements.txt
# Alternatively, using uv:
uv sync
```

## Configuration
No external configurations or API keys are required for the simulated environment.

## Running the Project

To launch the real-time SRE Dashboard:
```bash
streamlit run dashboard/app.py
```

## Running Tests

Tests are structured natively using pytest.
```bash
pytest -q
```

## Running Benchmarks

```bash
pytest tests/test_benchmarker.py
```

## Limitations

- Current environment is primarily simulated.
- Kubernetes integration may be experimental.
- Production observability integrations are not enabled by default.
- LLM performance depends on the selected model (currently mocked internally for testing without API keys).
- Benchmark results depend on incident distribution.
- Simulation results should not be interpreted as real production MTTR.

## Roadmap

* **Phase 1**: Core simulation + incident response (Completed)
* **Phase 2**: Improved agent reasoning + memory
* **Phase 3**: Real observability integrations
* **Phase 4**: Kubernetes integration
* **Phase 5**: Large-scale agent benchmarking

## Research / Engineering Value

AutoSRE serves as a highly modular foundation for studying the safety and efficacy of AI in critical infrastructure. By forcing the agent to prove its reasoning against a stateful environment, the project moves beyond text summarization into true agentic systems engineering.

## Contributing

Contributions are welcome. Please ensure that tests pass (`pytest -q`) and that new modules preserve the state-driven simulation architecture.

## License

MIT
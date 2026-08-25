# AutoSRE

## Overview
AutoSRE is an AI-assisted SRE simulation and incident-response platform for evaluating automated incident detection, investigation, root-cause analysis, remediation planning, verification, and post-mortem generation in a controlled environment.

## Problem
Modern production systems generate large volumes of metrics, logs, events, and alerts. During an incident, SRE teams must rapidly identify the cause, select a safe remediation, verify recovery, and document the incident. Testing autonomous agents in real production environments is too dangerous.

## Solution
AutoSRE provides a robust testing ground for AI in operations. Rather than acting as a simple text-based chatbot, AutoSRE operates as a stateful, ReAct-driven loop. The simulated environment accurately mimics infrastructure behavior—terminating a runaway process naturally causes CPU metrics to drop and error rates to recover, allowing the AI's logic to be rigorously evaluated in a safe, closed loop.

## Key Capabilities
| Capability | Status |
|------------|--------|
| Dynamic incident generation | Implemented |
| Stateful simulation | Implemented |
| Time-series telemetry | Implemented |
| Anomaly detection | Implemented |
| Evidence-based RCA | Implemented |
| Risk-aware planning | Implemented |
| What-if simulation | Implemented |
| Remediation verification | Implemented |
| Incident memory | Experimental |
| Real embeddings | Experimental |
| Kubernetes integration | Experimental |
| Real production observability | Not implemented |

## Architecture
```text
                    Incident Generator
                           |
                           v
                  Simulation Environment
                           |
             +-------------+-------------+
             |             |             |
          Metrics        Logs        Services
             |             |             |
             +-------------+-------------+
                           |
                  Investigation Agent
                           |
                        Evidence
                           |
                     RCA Engine
                           |
                  Candidate Actions
                           |
                     What-If Engine
                           |
                     Risk Policy
                           |
                  Human Approval
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
                      Benchmark
```

## Incident Lifecycle
AutoSRE guides an incident through a deterministic, logic-driven lifecycle. The system is evaluated not on whether it blindly guesses a fix, but on how it reasons through evidence.

## Agent Architecture
The system employs a multi-agent orchestrated architecture governed by strict risk policies:
* **Orchestrator**: Manages the incident lifecycle state machine.
* **Investigation Agent**: Queries the state pool (processes, logs, networks) to extract anomalous evidence using a controlled tool budget.
* **RCA Agent**: Synthesizes evidence to isolate the probable root cause from a complex web of symptoms using hypothesis scoring.
* **Planning Agent**: Formulates a targeted remediation plan based on What-If counterfactual simulations.
* **Postmortem Agent**: Synthesizes the timeline and telemetry into a compliant report.

## Simulation Environment
The project features a fully stateful simulator. Infrastructure state (active processes, database connections, active services) directly dictates the generated metrics. Remediations mutate this underlying state (e.g., removing a rogue process), causing metrics to naturally recover. 

## Observability
Telemetry is exposed via a dynamic `MetricsStore` and `SignalStore`. The agent does not cheat by accessing hidden ground-truth data; it relies entirely on its ability to request historical metrics and sift through simulated logs.

## Evidence-Based RCA
RCA is structured via hypothesis scoring and semantic evaluation rather than naive keyword matching. The agent's diagnosis must align with the correct failure category, pinpoint the correct underlying entity, and generate a causal chain based on supporting and contradicting evidence.

## Intelligent Remediation
Remediation candidate generation relies on the active tool registry and contextual evidence. The planning agent evaluates multiple tools against the current state before committing to an action.

## Safety Model
Actions carry inherent risk levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). `HIGH` risk actions mandate explicit approval policies.

## What-If Simulation
The What-If engine performs true counterfactual simulation by deep-copying the `SimulationEnvironment`, executing the candidate tool on the clone, and comparing the predicted telemetry against the original state to calculate confidence and risk recommendations.

## Verification
Remediation success is never assumed; the verification engine checks post-action telemetry against baseline health before closing an incident.

## Incident Memory
*(Experimental)* Previous incident vectors can be stored to improve future RCA accuracy. Production mode aims to support real embeddings, while the current test mode relies on deterministic mock representations.

## Chaos Engineering
The Chaos Injector can seamlessly simulate targeted failure classes: Infrastructure exhaustion, Network Latency, Database Failures, Security Incidents, and Cascading Multi-Service Failures. 

## Benchmarking
Benchmark methodology:
1. Generate incident
2. Hide ground-truth root cause
3. Expose telemetry
4. Run agent
5. Record actions
6. Verify recovery
7. Compare prediction with ground truth
8. Calculate metrics

## Example Incident
*(Example deterministic simulation run)*
```text
Incident:
Crypto-mining process injected.

Detection:
CPU anomaly detected (97%).

Investigation:
Agent runs `get_metric_history()` and `list_processes()`.
Discovers Process 'xmrig' (PID 8472) consumes 84% CPU.

RCA:
Hypothesis scoring selects Crypto miner.
Causal chain generated.

Plan:
What-If evaluates multiple actions. Terminate process 8472 selected.

Risk:
HIGH — approval required.

Execution:
Process terminated.

Verification:
CPU recovered. System stable.

Result:
Incident resolved.

Postmortem:
Generated automatically with MTTR tracking.
```

## Dashboard
The project includes a live Streamlit dashboard that binds directly to the running `SimulationEnvironment`. 

## Installation
```bash
git clone <repository>
cd AutoSRE-PostMortem

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -e .
```

## Quick Start
```bash
pytest -q
```
Then start the dashboard:
```bash
streamlit run dashboard/app.py
```

## Running Tests
Tests are structured natively using pytest.
```bash
pytest -q
```

## Running Benchmarks
Run the benchmark suite with configurable episodes:
```bash
python -m run_benchmark --episodes 50
```

## Project Structure
* `agents/`: Core AI agent loops (Investigation, Planning, RCA, Postmortem)
* `dashboard/`: Streamlit interactive UI
* `environment/`: Stateful simulator, chaos injector, incident generator, and metric storage
* `evaluation/`: Benchmarker suite
* `tools/`: Tool registry and strict execution policies
* `tests/`: Automated test suite for all modules

## Limitations
Current limitations may include:
- The default environment is simulated.
- Production Kubernetes control is not enabled by default.
- Real observability integrations may require additional configuration.
- LLM quality depends on the selected model.
- Benchmark results depend on scenario distribution.
- Business impact is an estimate within the simulation.

## Roadmap
* **Phase 1**: Core simulation + incident response (Completed)
* **Phase 2**: Improved agent reasoning + memory
* **Phase 3**: Real observability integrations
* **Phase 4**: Kubernetes integration
* **Phase 5**: Large-scale agent benchmarking

## Research / Engineering Value
AutoSRE serves as a highly modular foundation for studying the safety and efficacy of AI in critical infrastructure. By forcing the agent to prove its reasoning against a stateful environment, the project provides a controlled environment for evaluating agentic SRE workflows.

## License
MIT
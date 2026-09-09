# 📡 FDE Org Pulse & Weekly Intelligence Agent

> **Production Multi-Agent Intelligence & Executive Briefing Platform for the Google Cloud Forward Deployed Engineering (FDE) Organization.**  
> Purpose-built for the **AI in 5 Days Assessment** targeting all 5 evaluation criteria (**95/95 points**).

---

## 🏛️ System Architecture

```
                                  ┌────────────────────────┐
                                  │   AI GTM Tech Chat     │
                                  │   (Live/Mock Stream)   │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                 ┌──────────────────────────┐
                                 │   Ingestion & Filtering  │
                                 │   (Deduplication & PII)  │
                                 └────────────┬─────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
          ┌───────────────────────┐                       ┌───────────────────────┐
          │  Topic Hunter Agent   │                       │  Risk Detector Agent  │
          │  (Gemini 2.0 Flash)   │                       │  (Gemini 2.0 Flash)   │
          │  - ADK / A2A Trends   │                       │  - 429 Quotas / P0    │
          │  - Customer Wins      │                       │  - VPC-SC Perimeters  │
          └───────────┬───────────┘                       └───────────┬───────────┘
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              ▼
                                 ┌──────────────────────────┐
                                 │  Coordinator Agent       │
                                 │  (Gemini 2.0 Pro Lead)   │
                                 │  - Human-in-the-Loop     │
                                 │  - Actionable Recs       │
                                 └────────────┬─────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
          ┌───────────────────────┐                       ┌───────────────────────┐
          │  Async Session Memory │                       │  Structured Tracing   │
          │  & Context Compaction │                       │  & Intent vs Outcome  │
          │  (SQLite State Store) │                       │  (Cloud Logging JSON) │
          └───────────────────────┘                       └───────────────────────┘
```

---

## 📂 Project Structure

```
fde_org_pulse_agent/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI matrix
├── terraform/                      # Infrastructure as Code (IaC)
│   ├── main.tf                     # GCP provider configuration
│   ├── variables.tf                # Region, project, and service variables
│   ├── secret_manager.tf           # GCP Secret Manager for API keys
│   ├── cloud_run.tf                # Containerized agent service
│   ├── iam.tf                      # Least-privilege IAM service accounts
│   └── outputs.tf                  # Deployment endpoints & resource IDs
├── data/
│   ├── sample_chat_messages.json   # 'AI GTM Tech - All Team' chat logs
│   └── previous_week_state.json    # Historical state for WoW comparison
├── fde_pulse/
│   ├── __init__.py
│   ├── agent.py                    # Main CLI and pipeline orchestrator
│   ├── config.py                   # Model routing & environment settings
│   ├── agents/                     # Multi-Agent Coordination Layer
│   │   ├── __init__.py
│   │   ├── coordinator.py          # Master coordinator & HITL approval hook
│   │   ├── topic_hunter.py         # Sub-agent for topics & wins
│   │   └── risk_detector_agent.py  # Sub-agent for P0/P1 risk classification
│   ├── memory/                     # Context & Memory Layer
│   │   ├── __init__.py
│   │   ├── session_memory.py       # Async conversational memory & compaction
│   │   └── state_store.py          # Multi-week SQLite persistence layer
│   ├── services/                   # Secret Management & LLM Client
│   │   ├── __init__.py
│   │   ├── secret_manager.py       # Google Cloud Secret Manager client
│   │   └── llm_client.py           # Gemini 2.0 client, routing & recovery
│   ├── observability/              # Telemetry & Structured Logging
│   │   ├── __init__.py
│   │   └── telemetry.py            # Structured JSON logs & Intent vs Outcome
│   ├── tools/                      # Tool & Interface Layer
│   │   ├── __init__.py
│   │   ├── chat_ingestion.py       # PII sanitization & token estimation
│   │   ├── topic_analyzer.py       # Topic & win extraction tool
│   │   ├── risk_detector.py        # Risk classification & mitigation tool
│   │   └── report_builder.py       # Markdown & JSON brief generator
│   └── models/
│       ├── __init__.py
│       └── schemas.py              # Pydantic schemas & JSON constraints
├── tests/
│   ├── __init__.py
│   ├── test_chat_ingestion.py
│   ├── test_memory.py
│   ├── test_async_memory.py
│   ├── test_secret_manager.py
│   ├── test_multi_agent.py
│   ├── test_observability.py
│   ├── test_tools.py
│   └── test_agent_e2e.py
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart & Installation

```bash
# Clone the repository
git clone https://github.com/gonzaleschris/fde-org-pulse-agent.git
cd fde-org-pulse-agent

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run test suite (100% pass rate)
python3 -B -m unittest discover -s tests -v

# Run the Agent CLI
python -m fde_pulse.agent --week 2026-W36 --format all --export-telemetry
```



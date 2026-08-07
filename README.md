```
███████╗ ██████╗ ██████╗ ███████╗ ██████╗ █████╗ ███████╗████████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝
█████╗  ██║   ██║██████╔╝█████╗  ██║     ███████║███████╗   ██║
██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║     ██╔══██║╚════██║   ██║
██║     ╚██████╔╝██║  ██║███████╗╚██████╗██║  ██║███████║   ██║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝
```

# FORECAST — Agentic Financial Model Auditor

> **A multi-agent AI system that ingests startup financial models (Excel/CSV) and produces investor-grade audit reports — powered by LangGraph orchestration and NVIDIA Nemotron LLM.**

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="LangGraph" src="https://img.shields.io/badge/LangGraph-0.4.1-1C3C3C">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="NVIDIA NIM" src="https://img.shields.io/badge/NVIDIA%20NIM-Nemotron%203%20Super%20120B-76B900?logo=nvidia&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-Educational-lightgrey">
</p>

---

## 🎥 Video Demo

> **YouTube:** `https://youtu.be/WkJoQr_kiMo?si=ebXWUhBomfv7rrEs` 

<p align="left">
  <a href="https://youtu.be/WkJoQr_kiMo?si=ebXWUhBomfv7rrEs">
    <img src="https://img.shields.io/badge/▶-Watch%20the%20Demo%20on%20YouTube-FF0000?logo=youtube&logoColor=white&style=for-the-badge" alt="Watch the FORECAST demo on YouTube">
  </a>
</p>

A full walkthrough of the FORECAST pipeline — uploading a startup financial model, watching the 7-agent audit run in real time, and reviewing the generated investor-ready report.

---

## What is FORECAST?

FORECAST is an **autonomous financial model auditing platform** built for the venture capital and startup ecosystem. When a startup raises funding, investors receive Excel-based financial projections — revenue forecasts, burn rate models, cap tables, and cash flow statements. Today, validating these models is a **manual, error-prone process** that takes analysts 4–8 hours per model.

FORECAST replaces that workflow with an **agentic AI pipeline** that:

1. **Ingests** the uploaded Excel file and parses every cell, formula, and cross-sheet reference into a dependency graph.
2. **Deploys 7 specialized AI agents** in sequence — each focused on a specific audit dimension (structural integrity, assumptions, benchmarks, consistency, scenarios, cap table, and report generation).
3. **Produces** an investor-ready audit report (PDF/DOCX) with cell-level references, severity classifications, and actionable findings — in under 2 minutes.

### Industry Relevance

| Stakeholder | Pain Point FORECAST Solves |
|---|---|
| **VC Analysts** | Reduces financial model review from 4–8 hours to < 2 minutes |
| **Startup CFOs** | Self-audit before fundraise — catch errors before investors do |
| **Audit Firms** | Scalable pre-screening of client financial projections |
| **PE Due Diligence** | Automated first-pass on portfolio company models |
| **Angel Investors** | Solo investors without analyst teams get institutional-grade audits |

The global financial audit market is valued at **$280B+** (2024), with startup due diligence representing a fast-growing segment. FORECAST targets the intersection of **FinTech × Agentic AI**, a space where manual processes are ripe for disruption.

---

## The Agent Pipeline

FORECAST uses **7 specialized agents** orchestrated by LangGraph into a sequential pipeline with conditional branching:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FORECAST AUDIT PIPELINE                                  │
│                     (LangGraph State Machine)                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ┌──────────┐    ┌────────────┐    ┌────────────┐    ┌───────────┐             │
│   │ INGEST   │───▶│ STRUCTURAL │───▶│ ASSUMPTION │───▶│ BENCHMARK │            │
│   │          │    │            │    │            │    │           │             │
│   │ Parse    │    │ Formula    │    │ Extract    │    │ Compare   │             │
│   │ Excel    │    │ Forensics  │    │ Key Metrics│    │ vs Sector │             │
│   │ Build    │    │ Circular   │    │ Growth %   │    │ Comps     │             │
│   │ Dep Graph│    │ Refs       │    │ CAC, Churn │    │           │             │
│   └──────────┘    └────────────┘    └────────────┘    └───────────┘             │
│        │                                                    │                   │
│        ▼                                                    ▼                   │
│   ┌──────────────┐    ┌──────────┐                  ┌───────────┐               │
│   │ CONSISTENCY  │───▶│ SCENARIO │──────┬──────────▶│  REPORT   │──▶ END      │
│   │              │    │          │      │           │           │               │
│   │ Cross-Sheet  │    │ ±20%     │      │ No Cap    │ Generate  │               │
│   │ Reconcile    │    │ Sensitiv │      │ Table     │ PDF/DOCX  │               │
│   │ Balance Chk  │    │ Analysis │      │           │ Markdown  │               │
│   └──────────────┘    └──────────┘      │           └───────────┘               │
│                                         │                 ▲                     │
│                                         │ Has Cap         │                     │
│                                         │ Table?          │                     │
│                                         ▼                 │                     │
│                                    ┌──────────┐           │                     │
│                                    │ CAP TABLE│───────────┘                     │
│                                    │          │                                 │
│                                    │ Ownership│                                 │
│                                    │ Dilution │                                 │
│                                    │ SAFE Conv│                                 │
│                                    └──────────┘                                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Agent Details

| # | Agent | What It Does | Uses LLM? |
|---|-------|-------------|-----------|
| 1 | **Ingestion** | Parses every cell in the Excel workbook using `openpyxl`. Builds a directed dependency graph with `networkx` to map formula relationships across sheets. Identifies sheet types (P&L, Balance Sheet, Cap Table, etc.). | No — Pure algorithmic |
| 2 | **Structural** | Detects formula anomalies: circular references (graph cycle detection), hardcoded values in formula ranges, `#REF!`/`#DIV/0!` errors, inconsistent formula patterns in adjacent cells. Uses the LLM to classify ambiguous edge cases. | Yes — Nemotron |
| 3 | **Assumption** | Extracts key financial assumptions — growth rates, churn, CAC, LTV, margins, burn rate, runway — using regex pattern matching first, then falls back to LLM for natural-language label interpretation. | Yes — Nemotron |
| 4 | **Benchmark** | Compares extracted assumptions against industry benchmarks for the company's sector. Uses the LLM to reason about whether metrics are aggressive, conservative, or within healthy ranges. | Yes — Nemotron |
| 5 | **Consistency** | Cross-sheet reconciliation engine. Checks Revenue ↔ P&L ↔ Cash Flow linkage, verifies Balance Sheet balances (Assets = Liabilities + Equity), detects unit/currency mismatches (INR vs USD, monthly vs annual). | No — Pure algorithmic |
| 6 | **Scenario** | Perturbs key assumptions by ±20% and uses the `formulas` library to **genuinely re-evaluate Excel formulas** (not LLM estimation). Measures sensitivity of output metrics like Runway, EBITDA, and ARR. | No — Pure algorithmic |
| 7 | **Cap Table** *(conditional)* | Only runs if a cap table sheet is detected. Validates ownership percentages sum to 100%, checks option pool sizing, dilution math, and SAFE/convertible note conversion logic. | Yes — Nemotron |
| 8 | **Report** | Synthesizes all findings into a structured, investor-ready Markdown report. Generates downloadable PDF and DOCX versions with cell-level references and severity classifications. | Yes — Nemotron |

---

## Why LangChain / LangGraph?

### The Problem with Simple Scripts

A naive approach would chain function calls in a Python script: `parse() → analyze() → report()`. This breaks down because:

- **State management** — 7 agents produce different output types (lists of anomalies, dicts of assumptions, markdown strings). Each agent needs to read outputs from previous agents and append its own.
- **Conditional routing** — The cap table agent should only run if a cap table sheet exists. This requires runtime branching.
- **Error isolation** — If one agent fails, the pipeline should continue (with degraded output), not crash entirely.
- **Observability** — You need to track which agent is currently running for the progress bar UI.

### How LangGraph Solves This

**LangGraph** (from the LangChain ecosystem) provides a **state machine abstraction** purpose-built for multi-agent workflows:

```
                    ┌──────────────────────────────────────────┐
                    │           LangGraph StateGraph           │
                    │                                          │
                    │   AuditState (TypedDict)                 │
                    │   ┌──────────────────────────────────┐   │
                    │   │ file_path: str                    │   │
                    │   │ formula_anomalies: list[dict]     │   │  ← Append-only
                    │   │ assumptions: list[dict]           │   │    via operator.add
                    │   │ scenario_results: list[dict]      │   │    reducer
                    │   │ report_markdown: str              │   │
                    │   │ current_agent: str                │   │
                    │   │ ...                               │   │
                    │   └──────────────────────────────────┘   │
                    │                                          │
                    │   Nodes: ingestion, structural, ...      │
                    │   Edges: sequential + conditional        │
                    │   Execution: async (ainvoke)             │
                    └──────────────────────────────────────────┘
```

| LangGraph Feature | How FORECAST Uses It |
|---|---|
| **`StateGraph`** | Defines the pipeline as a directed graph of agent nodes |
| **`TypedDict` state** | `AuditState` — a shared typed dictionary that flows through all nodes |
| **`Annotated[list, operator.add]`** | Append-only reducers — each agent returns only its new findings, LangGraph merges them |
| **`add_conditional_edges`** | Routes to Cap Table agent only when `has_cap_table == True` |
| **`ainvoke`** | Async execution — the entire pipeline runs non-blocking |
| **`START` / `END`** | Built-in entry/exit points for the state machine |

### What About LangChain?

FORECAST uses **`langchain-core`** (not the full LangChain framework) for:

- **`ChatOpenAI`-compatible client** — The NVIDIA NIM API follows the OpenAI chat completions format. LangChain's client abstractions handle retries, streaming, and message formatting.
- **Message types** — `SystemMessage`, `HumanMessage` for structured prompt construction.

We intentionally avoid the heavier LangChain abstractions (chains, retrievers, memory) since our agents are specialized and don't need generic tool-calling or RAG patterns.

---

## n8n Workflow Integration

### What is n8n?

[n8n](https://n8n.io) is an open-source workflow automation platform (similar to Zapier or Make, but self-hosted). It provides a visual, node-based editor for building automation workflows that connect different services — email, Slack, databases, APIs, spreadsheets, and more.

### Why FORECAST Uses n8n

The core LangGraph pipeline handles the **analytical heavy-lifting** — parsing Excel files, detecting anomalies, running scenarios. But after an audit completes, there are **downstream business actions** that vary by organization:

- Email the PDF report to the deal team
- Post a Slack summary to the `#due-diligence` channel
- Update a CRM (HubSpot, Salesforce) with the audit status
- Log the audit in an Airtable or Google Sheets tracker
- Trigger a follow-up task in Jira or Linear
- Archive the report to Google Drive or S3

These post-audit actions are **not part of the core audit logic** and change frequently depending on the team's tooling. Hardcoding them into the Python backend would create tight coupling and require redeployment for every change. n8n solves this by externalizing the automation layer.

### How It Works

```
  FORECAST Backend                          n8n (self-hosted)
  ================                          =================

  Audit completes
       |
       v
  POST webhook ──────────────────────> /webhook/forecast-audit-complete
  {                                         |
    job_id,                                 v
    company_name,                    ┌──────────────┐
    report_url                       │ Webhook Node │
  }                                  └──────┬───────┘
                                            |
                                            v
                                    ┌───────────────┐
       POST /audit/{id}/n8n-status  │ Your Workflow │
       <────────────────────────────│               │
       { status: "Sending Email" }  │  Email Node   │
                                    │  Slack Node   │
       POST /audit/{id}/n8n-status  │  CRM Node     │
       <────────────────────────────│  ...          │
       { status: "Workflow Complete"}└───────────────┘
                                            |
                                    Dashboard shows
                                    real-time status
```

### The Data Flow

1. **Trigger** — When the LangGraph pipeline finishes, the `JobManager` fires an async HTTP POST to the n8n webhook URL (`http://localhost:5678/webhook/forecast-audit-complete`) with the `job_id`, `company_name`, and `report_url`.

2. **n8n Processes** — The n8n workflow receives the payload and executes whatever automation nodes you've configured (email, Slack, CRM updates, etc.).

3. **Status Callbacks** — As n8n progresses through each step, it calls back to FORECAST's API (`POST /api/audit/{job_id}/n8n-status`) with status updates like `"Sending Email"`, `"Updating CRM"`, `"Workflow Complete"`.

4. **Dashboard Display** — The frontend Workflow page polls the status endpoint and displays the n8n workflow progress in real-time, including the current stage name and a completion indicator.

### Use Cases

| Workflow | n8n Nodes Used | Description |
|---|---|---|
| **Email Report to Team** | Webhook + Email (SMTP/Gmail) | Auto-send the PDF audit report to the deal lead |
| **Slack Alert** | Webhook + Slack | Post a summary with critical finding count to a channel |
| **CRM Update** | Webhook + HubSpot/Salesforce | Update the deal stage with audit completion status |
| **Google Sheets Log** | Webhook + Google Sheets | Append a row with audit metadata for tracking |
| **Conditional Escalation** | Webhook + IF + Email | If critical findings > 3, escalate to the partner |
| **Archive to Cloud** | Webhook + HTTP + S3/GDrive | Download the PDF and archive it in cloud storage |

### Running Without n8n

n8n is **entirely optional**. If no n8n instance is running, the webhook call silently fails (caught and logged as a warning), and the audit completes normally. The Workflow page will simply show `"pending"` status. The core audit functionality is completely independent.

### Setting Up n8n (Optional)

```bash
# Quick start with Docker
docker run -it --rm -p 5678:5678 n8nio/n8n

# Open n8n at http://localhost:5678
# Create a workflow starting with a Webhook node
# Set the webhook path to: /webhook/forecast-audit-complete
# Add downstream nodes (Email, Slack, HTTP Request for status callbacks, etc.)
```

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.115 | Async REST API framework |
| **Uvicorn** | 0.34 | ASGI server |
| **LangGraph** | 0.4.1 | Multi-agent pipeline orchestration |
| **LangChain Core** | 0.3.55 | LLM client abstractions |
| **NVIDIA NIM** | — | LLM inference (Nemotron 120B) |
| **OpenPyXL** | 3.1.5 | Excel parsing (.xlsx) |
| **Formulas** | 1.3.4 | Excel formula re-evaluation engine |
| **NetworkX** | 3.4.2 | Dependency graph / cycle detection |
| **SQLAlchemy** | 2.0 (async) | ORM + database layer |
| **aiosqlite** | 0.21 | Async SQLite driver |
| **ReportLab** | 4.4 | PDF generation |
| **python-docx** | 1.1 | DOCX generation |
| **httpx** | 0.28 | Async HTTP client |
| **Tenacity** | 9.1 | Retry logic with exponential backoff |
| **Pydantic** | v2 | Data validation + settings |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **React** | 19 | UI framework |
| **Vite** | 8.2 | Build tool + dev server |
| **React Router** | 7.18 | Client-side routing |
| **Recharts** | 3.10 | Sensitivity analysis charts |
| **Lucide React** | 1.28 | Icon library |
| **Axios** | 1.19 | HTTP client for API calls |
| **react-dropzone** | 20.0 | Drag-and-drop file upload |

### Infrastructure

| Component | Technology |
|---|---|
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **LLM Provider** | NVIDIA NIM API (Nemotron 3 Super 120B) |
| **File Storage** | Local filesystem (`uploads/`, `reports/`) |

---

## Features

| Feature | Description |
|---------|-------------|
| **Formula Forensics** | Broken refs, hardcoded values in formulas, inconsistent patterns, #REF!/#DIV0! errors |
| **Circular Reference Detection** | Graph-based cycle detection across the full dependency graph |
| **Assumption Extraction** | Regex + LLM fallback for pulling growth %, churn, CAC, LTV, margins, burn, runway |
| **Sector Benchmarking** | Compares extracted assumptions against industry comps via LLM reasoning |
| **Cross-Sheet Consistency** | Revenue/P&L/Cash Flow reconciliation, balance sheet balance check |
| **Unit/Currency Detection** | Mixed INR/USD, ₹L/₹Cr, monthly/annual mismatches |
| **Scenario Sensitivity** | Real formula re-evaluation (±20%) via `formulas` library — not LLM guessing |
| **Cap Table Validation** | Ownership sum, option pool sizing, dilution math, SAFE conversion |
| **PDF/DOCX Reports** | Auto-generated investor-ready audit reports with cell references |
| **Version Diffing** | Compare model v1 vs v2, see what assumptions changed |
| **Audit History** | SQLite-backed history with trend view per company |
| **Delete Audits** | Remove audit runs from history |
| **Demo Mode** | Toggle fake data on/off for UI testing and demos |

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **NVIDIA NIM API Key** — free at [build.nvidia.com](https://build.nvidia.com)

### 1. Clone & Configure

```bash
git clone https://github.com/Jilu-Jose/Project-FORECAST.git
cd Project-FORECAST
cp .env.example .env
```

Edit `.env` and add your NVIDIA NIM API key:

```env
NVIDIA_NIM_API_KEY="nvapi-your-key-here"
NVIDIA_NIM_MODEL="nvidia/nemotron-3-super-120b-a12b"
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Start Backend

```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 5. Open Dashboard

Visit **http://localhost:5173** → upload an Excel model → watch the audit run.

---

## Project Structure

```
Project-FORECAST/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic settings from .env
│   │   ├── agents/              # LangGraph agent nodes
│   │   │   ├── graph.py         # Pipeline wiring (StateGraph)
│   │   │   ├── state.py         # AuditState TypedDict definition
│   │   │   ├── ingestion.py     # Excel parsing + dependency graph
│   │   │   ├── structural.py    # Formula anomaly detection (NIM)
│   │   │   ├── assumption.py    # Key metric extraction (NIM)
│   │   │   ├── benchmark.py     # Sector benchmark comparison (NIM)
│   │   │   ├── consistency.py   # Cross-sheet reconciliation
│   │   │   ├── scenario.py      # ±20% sensitivity analysis
│   │   │   ├── captable.py      # Equity structure validation (NIM)
│   │   │   └── report.py        # Narrative report generation (NIM)
│   │   ├── api/                 # REST endpoint routers
│   │   │   ├── audit.py         # Upload, status, report endpoints
│   │   │   └── history.py       # History, diff, delete endpoints
│   │   ├── models/               # Data models
│   │   │   ├── database.py      # SQLAlchemy ORM models
│   │   │   └── schemas.py       # Pydantic validation schemas
│   │   ├── services/            # Business logic services
│   │   │   ├── llm.py           # NVIDIA NIM client wrapper
│   │   │   ├── spreadsheet.py   # Excel parsing engine
│   │   │   └── report_gen.py    # PDF/DOCX generation
│   │   └── utils/               # Utilities
│   │       └── formula_tokenizer.py
│   └── tests/
│       ├── create_test_fixture.py
│       └── fixtures/
│           └── sample_model.xlsx
├── frontend/                     # React + Vite dashboard
│   └── src/
│       ├── api/client.js         # API client + demo data
│       ├── pages/                # Route pages
│       │   ├── Ingestion.jsx     # File upload + recent uploads
│       │   ├── Overview.jsx      # Audit dashboard
│       │   ├── Findings.jsx      # Detailed findings table
│       │   ├── Scenarios.jsx     # Sensitivity analysis charts
│       │   ├── Reports.jsx       # Markdown report viewer
│       │   ├── Workflow.jsx      # Pipeline status tracker
│       │   └── History.jsx       # Audit history list
│       └── components/           # Reusable UI components
│           ├── Sidebar.jsx       # Navigation sidebar
│           ├── Header.jsx        # Top bar + demo toggle
│           ├── Loader.jsx        # Animated loading state
│           ├── FindingsTable.jsx # Severity-colored findings
│           ├── SensitivityChart.jsx # Recharts bar chart
│           └── SeverityBadge.jsx # Badge component
├── .env.example                  # Environment variable template
├── .gitignore
└── README.md
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audit/upload` | POST | Upload Excel file and start audit pipeline |
| `/api/audit/status/{id}` | GET | Poll audit progress (agent name, % complete) |
| `/api/audit/report/{id}` | GET | Get full findings + report data |
| `/api/audit/report/{id}/download?format=pdf` | GET | Download PDF or DOCX report |
| `/api/audit/{id}` | DELETE | Delete an audit run |
| `/api/history` | GET | List all audits (paginated) |
| `/api/history/{company}` | GET | Company-specific audit history |
| `/api/diff/{id1}/{id2}` | GET | Version comparison between two audits |

---

## Security Notes

- **API keys** are stored in `.env` (gitignored — never committed)
- **SQLite database** (`forecast.db`) is gitignored — contains audit results and uploaded data references
- **Uploaded files** (`uploads/`) are gitignored
- **Generated reports** (`reports/`) are gitignored
- All LLM calls use HTTPS via the NVIDIA NIM API

---

## License

This project is for educational and demonstration purposes.
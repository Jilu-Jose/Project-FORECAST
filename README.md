# FORECAST — Agentic Financial Model Auditor

> Multi-agent system that ingests startup financial models (Excel) and produces investor-grade audit reports.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Formula Forensics** | Broken refs, hardcoded values in formulas, inconsistent patterns, #REF!/#DIV0! errors |
| 🔄 **Circular Reference Detection** | Graph-based cycle detection across the full dependency graph |
| 📊 **Assumption Extraction** | Regex + LLM fallback for pulling growth %, churn, CAC, LTV, margins, burn, runway |
| 🌐 **Web-Grounded Benchmarks** | Gemini + Google Search compares assumptions against real sector comps |
| 🔗 **Cross-Sheet Consistency** | Revenue/P&L/Cash Flow reconciliation, balance sheet balance check |
| 💱 **Unit/Currency Detection** | Mixed INR/USD, ₹L/₹Cr, monthly/annual mismatches |
| 📈 **Scenario Sensitivity** | Real formula re-evaluation (±20%) via `formulas` library — not LLM guessing |
| 🏛️ **Cap Table Validation** | Ownership sum, option pool sizing, dilution math, SAFE conversion |
| 📄 **PDF/DOCX Reports** | Auto-generated investor-ready audit reports with cell references |
| 🗃️ **Version Diffing** | Compare model v1 vs v2, see what assumptions changed |
| 📋 **Audit History** | SQLite-backed history with trend view per company |

## 🏗️ Architecture

```
React Dashboard → FastAPI → LangGraph Pipeline → SQLite DB
                                ↓
            [Ingestion] → [Structural (NIM)] → [Assumption (NIM)]
                → [Benchmark (Gemini+Web)] → [Consistency]
                → [Scenario] → [Cap Table?] → [Report (Gemini)]
```

**Dual-model cost optimization:**
- **NVIDIA NIM (Nemotron)** — high-volume structural/extraction calls (cheap, parallel)
- **Google Gemini** — reasoning + web-grounded benchmark lookups only

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your NVIDIA_API_KEY and GEMINI_API_KEY
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Mac/Linux
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

## 📁 Project Structure

```
Project-FORECAST/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Settings
│   │   ├── agents/           # LangGraph agent nodes
│   │   │   ├── graph.py      # Pipeline wiring
│   │   │   ├── ingestion.py  # Parse Excel → dependency graph
│   │   │   ├── structural.py # Formula anomaly detection
│   │   │   ├── assumption.py # Key metric extraction
│   │   │   ├── benchmark.py  # Gemini web-grounded checks
│   │   │   ├── consistency.py# Cross-sheet reconciliation
│   │   │   ├── scenario.py   # ±20% perturbation analysis
│   │   │   ├── captable.py   # Equity structure validation
│   │   │   └── report.py     # Narrative report generation
│   │   ├── api/              # REST endpoints
│   │   ├── models/           # Pydantic + SQLAlchemy models
│   │   ├── services/         # LLM clients, spreadsheet parser, report gen
│   │   └── utils/            # Formula tokenizer
│   └── tests/
│       ├── create_test_fixture.py
│       └── fixtures/
│           └── sample_model.xlsx
├── frontend/                 # React/Vite dashboard
│   └── src/
│       ├── pages/            # Upload, AuditView, History
│       └── components/       # Navbar, FindingsTable, Charts
├── .env.example
└── README.md
```

## 🧪 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audit/upload` | POST | Upload Excel file, start audit |
| `/api/audit/status/{id}` | GET | Poll audit progress |
| `/api/audit/report/{id}` | GET | Get full findings + report |
| `/api/audit/report/{id}/download?format=pdf` | GET | Download PDF/DOCX |
| `/api/history` | GET | List all audits |
| `/api/history/{company}` | GET | Company audit history |
| `/api/diff/{id1}/{id2}` | GET | Version comparison |

## 💰 Cost Optimization

The dual-model strategy significantly reduces API costs:

| Operation | Model | Calls/Audit | Rationale |
|-----------|-------|-------------|-----------|
| Structural analysis | NIM (Nemotron) | 1-3 | Batch cell classification |
| Assumption extraction | NIM (Nemotron) | 1-2 | Label matching fallback |
| Cap table analysis | NIM (Nemotron) | 0-1 | Conditional execution |
| Benchmark checking | Gemini + Web | 3-5 | Requires web grounding |
| Report generation | Gemini | 1 | Narrative writing |

NIM handles ~80% of LLM calls at lower cost. Gemini is reserved for tasks requiring reasoning + web access.

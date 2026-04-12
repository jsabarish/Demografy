# Demografy Insights Chatbot

A natural-language chatbot that lets Demografy platform users query Australian demographic data. Ask questions in plain English — get instant, data-driven suburb insights.

**Built with:** Python · Streamlit · LangChain · Gemini 2.5 Flash-Lite · Google BigQuery · LangSmith

---

## What It Does

Users type questions like:
> "What are the top 3 suburbs in Victoria with the highest diversity index?"

The bot:
1. Translates the question into SQL using Gemini AI
2. Runs the query against Demografy's BigQuery database
3. Returns a clear text answer (with optional chart)

---

## Project Structure

```
demografy-insights/
├── app.py                    # Streamlit app — entry point
├── agent/
│   ├── sql_agent.py          # LangChain SQL agent (core AI logic)
│   └── prompts.py            # Few-shot examples + KPI mappings
├── auth/
│   └── rbac.py               # User tier lookup + question limits
├── db/
│   └── bigquery_client.py    # BigQuery connection wrapper
├── eval/
│   ├── golden_dataset.json   # 10 test Q&A pairs
│   ├── run_eval.py           # Automated evaluation script
│   └── judge.py              # LLM-as-a-judge scorer
├── .streamlit/
│   └── config.toml           # Demografy brand theme
├── .env.template             # Copy this to .env and fill in keys
├── requirements.txt          # Python dependencies
└── CHANGELOG.md              # Version history
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- A terminal (Mac: Terminal app or VS Code terminal)

### 2. Clone the repository
```bash
git clone <your-repo-url>
cd demografy-insights
```

### 3. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables
```bash
cp .env.template .env
```
Then open `.env` and fill in:
- `GOOGLE_APPLICATION_CREDENTIALS` — path to your BigQuery service account JSON file
- `GEMINI_API_KEY` — get free key at [aistudio.google.com](https://aistudio.google.com)
- `LANGCHAIN_API_KEY` — get free key at [smith.langchain.com](https://smith.langchain.com)

### 6. Run the app
```bash
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`

---

## Credentials Needed

| Credential | Where to Get It | Who Has It |
|---|---|---|
| BigQuery Service Account JSON | GCP Console → IAM → Service Accounts | Wayne (AI Head) |
| Gemini API Key | [aistudio.google.com](https://aistudio.google.com) — free | Self-serve |
| LangSmith API Key | [smith.langchain.com](https://smith.langchain.com) — free | Self-serve |

---

## User Tiers

| Tier | Questions per Session |
|---|---|
| Free | 5 |
| Basic | 20 |
| Pro | 50 |

---

## Data

- **Production table:** `demografy.prod_tables.a_master_view`
- **Customer table:** `demografy.ref_tables.dev_customers`
- **Coverage:** 2,329 Australian SA2 suburbs with 10 KPIs

### KPI Reference

| Column | Name | Range |
|---|---|---|
| kpi_1_val | Prosperity Score | 0–100% |
| kpi_2_val | Diversity Index | 0–1 |
| kpi_3_val | Migration Footprint | 0–100% |
| kpi_4_val | Learning Level | 0–100% |
| kpi_5_val | Social Housing | 0–100% |
| kpi_6_val | Resident Equity | 0–100% |
| kpi_7_val | Rental Access | 0–100% |
| kpi_8_val | Resident Anchor | 0–100% |
| kpi_9_val | Household Mobility Potential | 0–1 |
| kpi_10_val | Young Family Indicator | 0–100% |

---

## Security

- Never commit `.env` or any `*.json` key files to GitHub
- The SQL agent is restricted to read-only queries on `a_master_view` and `dev_customers` only
- Destructive SQL (DELETE, UPDATE, INSERT, DROP) is blocked by the agent prompt

---

## Version History

See [CHANGELOG.md](CHANGELOG.md)

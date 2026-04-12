# Changelog

All notable changes to this project are documented here.
Format: `[vX.Y.Z] — YYYY-MM-DD — Description`

---

## [v0.1.0] — 2026-04-12 — Project Scaffold

### Added
- Full project folder structure created
- `.gitignore` — excludes secrets (.env, *.json), Source/ folder, Python cache
- `requirements.txt` — all Python dependencies listed
- `.env.template` — safe-to-commit template for environment variables
- `CHANGELOG.md` — this file
- `README.md` — setup instructions and project overview

### Notes
- BigQuery connection not yet active (waiting for service account key)
- No code logic yet — structure only

---

## [v0.2.0] — 2026-04-12 — Core Code

### Added
- `db/bigquery_client.py` — BigQuery connection using service account credentials
- `db/explore.py` — data exploration script (run once after getting SA key)
- `agent/prompts.py` — KPI name→column mappings + 8 few-shot SQL examples
- `agent/sql_agent.py` — LangChain SQL agent wiring Gemini to BigQuery
- `auth/rbac.py` — user tier lookup + question limit enforcement
- `app.py` — full Streamlit app (login screen + chat UI + sidebar)
- `.streamlit/config.toml` — Demografy brand colours (purple theme)
- All packages installed in venv (Python 3.13)

### Changed
- `app.py` — redesigned to collapsible left info panel + full-width chat on right
- Left panel collapses to a thin strip with ▶/◀ toggle button

### Notes
- Gemini API key and LangSmith API key configured in .env
- BigQuery connection not yet testable (waiting for service account JSON from Wayne)
- Streamlit UI launches correctly — chat UI and collapsible panel working

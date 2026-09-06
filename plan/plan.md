# Project Export & Handoff Package — Plan

Goal: produce a single ZIP that another Emergent workspace (or any Streamlit host) can unpack and run without rebuilding. Also produce two handoff docs.

---

## What will be produced

1. **`/app/personal_finance_tracker_transfer.zip`** — the portable project.
2. **`/app/PROJECT_HANDOFF.md`** — architecture, features, business rules, OCR, responsive design, run instructions (in-repo, included inside the ZIP).
3. **`/app/CONTINUE_PROJECT_PROMPT.txt`** — a ready-to-paste prompt telling the next Emergent agent this project is already complete and how to iterate on it without rebuilding (included inside the ZIP).

The working app is not touched. Nothing is refactored, rebuilt, or renamed.

## What goes INTO the ZIP

Everything required to run:

- `app.py`, `webhook_server.py`
- Source folders: `pages_app/`, `services/`, `components/`, `database/`, `utils/`
- Bootstrap folders retained as-is: `backend/`, `frontend/`, `tests/`
- Support: `assets/`, `data/` (empty folder only — no `.db`, no `.jwt_secret`)
- Config: `requirements.txt`, `packages.txt`, `.streamlit/config.toml`, `.env.example`
- Docs: `README.md`, `PROJECT_HANDOFF.md`, `CONTINUE_PROJECT_PROMPT.txt`

## What is EXCLUDED from the ZIP

- Secrets & credentials: `data/finance.db`, `data/.jwt_secret`, any `.env` (only `.env.example`)
- Caches / build artefacts: `__pycache__/`, `.pytest_cache/`, `node_modules/`, `.venv/`, `*.pyc`, `.DS_Store`
- Platform-internal: `.emergent/`, `.git/`, `memory/`, `test_reports/`, `plan/`, `test_result.md`
- Lockfiles unrelated to the Streamlit app: `yarn.lock`

## Verification before finishing

- Sanity-check: unzip the archive to a scratch dir, run `python -c "import app"` in it to confirm imports resolve without the pod's site-packages leaking in (only checks syntax and structure — not a full smoke test).
- Print a manifest (top-level `ls`) so the user sees exactly what shipped.
- Report the ZIP file's absolute path and give the user two ways to fetch it (file browser download, or fetching via the preview URL if that turns out to work). If neither works cleanly, fall back to instructing them to use the "Save to GitHub" chat-input button on the current project — the receiving Emergent workspace can then clone that repo.

## Decision worth confirming

**The Emergent bootstrap `backend/` (FastAPI) and `frontend/` (React) folders are unused by this Streamlit app.** They exist because the pod was scaffolded as a full-stack template before the pivot to Streamlit. The user's list explicitly mentions them, so the plan is to **include them as-is** (no code inside them was written for this project). If the user would rather ship a leaner ZIP, they can be dropped; the Streamlit app doesn't reference them.

Default assumption: **include** — matches the user's checklist. Say so and this changes.

## Out of scope

- Any code change to the running app.
- Regenerating demo data (the new workspace will auto-seed the demo user on first launch of `streamlit run app.py`).
- Deploying anywhere; this is a packaging step only.

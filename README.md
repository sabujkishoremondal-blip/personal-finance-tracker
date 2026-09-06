# Personal Finance — Streamlit App

A polished, mobile-first personal money command center. Track balance, expenses, borrows/lends, monthly reports and get rule-based savings recommendations. Built with **Python + Streamlit + SQLite** and OCR via **Tesseract**.

## Features
- **Dashboard** with hero balance card, quick actions and category breakdown.
- **Add Expense** manually or by **uploading a payment screenshot** (OCR extracts amount, merchant, date, category).
- **Add Balance** (pocket money, salary, refund…) — increases available funds.
- **Borrow & Lend** — two-way tracking. Borrowed money increases balance; money friends owe does NOT increase balance until received.
- **Monthly Reports** — total spent, category share (donut + bar), monthly trend, comparisons.
- **Budget & Goals** — total & per-category budgets with progress bars; warnings, never blocks.
- **How Can I Save?** — rule-based recommendations from your own data with per-category next-month targets.
- **Settings** — name, currency (₹/₹/$/€…), theme toggle (light ivory / dark navy), categories, JSON + CSV export/import, database reset.
- **Negative balances allowed and clearly shown.**
- **Mobile-first responsive** design with cards on mobile and grids on desktop.
- **SQLite** as source of truth — session_state is only used for temporary UI state.

## Project structure
```
app.py
database/
    database.py        # sqlite init + settings
pages_app/
    dashboard.py
    expenses.py
    borrow_lend.py
    reports.py
    budget.py
    settings.py
components/
    theme.py           # CSS + palettes
    cards.py
    charts.py
services/
    expense_service.py
    balance_service.py
    ocr_service.py     # Tesseract
    analytics_service.py
    recommendation_service.py
    demo_service.py
utils/
    formatting.py
    constants.py
data/                 # SQLite lives here (created at runtime)
```

## Requirements
- Python 3.10+
- Tesseract OCR (system package)
- Packages in `requirements.txt`

## Install & run locally
```bash
# 1. system dependency for OCR
# Debian/Ubuntu:
sudo apt-get install -y tesseract-ocr
# macOS:
brew install tesseract

# 2. python dependencies
pip install -r requirements.txt

# 3. run
streamlit run app.py
```

Open http://localhost:8501

### Environment (`.env.example`)
`TESSERACT_CMD=/usr/bin/tesseract` — optional, only if tesseract is not on PATH.

## Deploy
### Streamlit Community Cloud
1. Push repo to GitHub.
2. Add `packages.txt` at the root with:
   ```
   tesseract-ocr
   ```
3. Deploy with app file = `app.py`.

### Replit
1. Import the repo.
2. Ensure the run command is:
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Add `tesseract-ocr` under `replit.nix` if needed.

### Emergent
Runs with `streamlit run app.py`. SQLite persists at `./data/finance.db` (relative path — no host-specific paths).

## Backups
- **Settings → Data export & import** provides:
  - JSON full backup (all tables)
  - CSV export of expenses
  - JSON restore
- **Reset database** wipes all data (confirmation required).

## Demo data
On first launch a small demo dataset is seeded (balance, expenses, one borrow, one lent). Reset the database in Settings to start fresh.

# Personal Finance (Streamlit) — PRD

## Original problem statement (summary)
Build a polished, mobile-first personal expense tracking web app using **Python + Streamlit + SQLite + Plotly + Tesseract OCR**. Two-way money tracking (balance, expenses, borrow, lend), monthly reports, budgets and rule-based savings recommendations. INR default, dark/light theme toggle, seeded demo data on first launch.

## User personas
- Single user, personal money management.
- Uses phone as primary device, occasionally desktop.
- Needs fast expense entry, monthly analysis and clarity on who owes whom.

## Core requirements (static)
1. SQLite persistence — never lose data on rerun.
2. Balance derived from transactions (no mutable stored value).
3. Borrowed money increases balance; money friends owe does NOT increase balance until received.
4. Negative balance allowed with clear warning; user never blocked.
5. Screenshot OCR extracts amount / merchant / date / suggested category; user MUST confirm before saving.
6. Mobile-first responsive, no horizontal scroll.
7. INR (₹) default, currency switchable.
8. Light (ivory + burgundy) and dark (navy + burgundy) themes with runtime toggle.

## Implemented (2026-09-06)
- **Architecture**: modular — `app.py` entry, `database/`, `services/`, `pages_app/`, `components/`, `utils/`.
- **Database (SQLite)**: `expenses`, `balance_transactions`, `debts`, `categories`, `budgets`, `app_settings`. Auto-init and seed default categories on first launch.
- **Dashboard**: hero balance card (light/dark burgundy gradient), 4 stat cards, 4 quick actions, category donut, recent transactions.
- **Expenses page**: 4 tabs — Add Expense, Add Balance, Scan Screenshot (Tesseract), History (filter/sort/search + edit/delete popover).
- **Borrow & Lend**: 3 tabs (I Borrowed, Friends Owe Me, + Add Entry). Confirm dialog before repay/receive. Balance math verified.
- **Reports**: metrics, donut, horizontal bar, monthly-trend line, MoM comparison narrative, rule-based savings tips with potential monthly saving and per-category next-month targets.
- **Budget & Goals**: total + per-category budgets, progress bars, over-budget warnings.
- **Settings**: name, currency (7 options), theme, starting balance, category CRUD, JSON+CSV export, JSON import, database reset with two-step confirmation.
- **Theme**: custom CSS with two palettes, Fraunces (display) + Manrope (body) fonts, no default Streamlit look.
- **OCR**: Tesseract-based extraction with amount / merchant / date / category heuristics. Manual override always allowed.
- **Demo data**: auto-seeds ~10 expenses, +₹500 balance, one borrow (Rahul ₹500), one lent (Priya ₹400) into the current month. Available balance on fresh install = ₹1,050.
- **Deployment**: `packages.txt` for Streamlit Cloud (tesseract-ocr), `.streamlit/config.toml`, README with Replit + Streamlit Cloud instructions. Running in Emergent preview via supervisor on port 3000.

## Testing
- Service-layer tests: 8/8 balance-math cases pass (`/app/backend/tests/test_balance_math.py`).
- E2E UI test (testing agent): expense add decreases balance correctly. All 6 pages render. No horizontal scroll at 390px. 100% success, no blocking bugs.

## Backlog / P1
- Persistent bottom-nav on mobile with FAB for Add Expense.
- Programmatic tab activation (Streamlit limitation — use session_state + radio workaround).
- Recurring expense templates.
- Multi-user auth (currently single-user local).

## P2 ideas
- LLM-powered richer savings narrative (currently rule-based).
- WhatsApp/Telegram bot to add expenses via chat.
- Cloud sync / backup to Google Drive.

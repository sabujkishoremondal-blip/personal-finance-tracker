# Personal Finance (Streamlit) — Project Handoff

A complete, polished, production-ready personal expense-tracking and money-management web app built with **Python + Streamlit + SQLite**. This document is the single source of truth for anyone (human or AI agent) picking up this project.

---

## 1. What this app is

A mobile-first, single-user (multi-account) personal money command center. When you open it you should immediately understand:

- **How much money do I have?**
- **How much have I spent this month?**
- **Where did it go?**
- **Who owes me money? Whom do I owe?**
- **Am I overspending? How can I spend less next month?**

Every question is answerable within seconds. The most common workflow (add an expense) takes 2–3 taps.

---

## 2. Feature list (all implemented and tested)

### Money & transactions
- Set an initial balance per user.
- Add balance additions (pocket money, salary, gift, …).
- Add expenses manually.
- **OCR-based screenshot expenses** — upload a UPI/receipt screenshot, Tesseract extracts amount + merchant + date + suggested category. User confirms before saving.
- **WhatsApp-style Quick Add chat** — type "Lunch 180 Food" or drop a receipt photo, expense is created immediately.
- Edit / delete any expense — balance always recalculates from transactions.
- Balance can go negative — clearly warned but never blocked.

### Borrow & Lend
- **I Borrowed** — money you received & must return. Increases your available balance.
- **Friends Owe Me** — money you paid on their behalf. Does **NOT** increase balance until marked as received.
- Mark as Repaid / Mark as Received with confirm dialogs.
- Net-to-receive summary card.

### Reports & analytics
- Monthly report: total spent, total funds, remaining, avg/day, top category, count.
- Category donut + horizontal bar chart.
- Monthly trend line (last 6 months) with MoM narrative ("Spending increased 15.7% — biggest driver: Outing").
- **How Can I Save?** — rule-based analysis of spending patterns with per-category next-month targets and potential monthly saving.

### Budgets & goals
- Total monthly budget + optional per-category budgets.
- Progress bars with over-budget warnings (never blocks).

### Recurring expenses
- Monthly (day-of-month) or weekly (day-of-week) rules with optional end date.
- **Auto-posts** on any app session once due dates are reached (idempotent via `last_run`).
- Pause / resume / delete.

### Auth & multi-user
- Custom email + password auth with **bcrypt** hashing.
- Session lives in `st.session_state` (no browser cookies needed for the Streamlit UI).
- **JWT tokens** issued for future WhatsApp webhook use.
- Each user's finances are **fully isolated** by `user_id` on every table.
- Change password, update profile, sign out.
- Demo account auto-seeded on first run: `demo@example.com` / `demo123`.

### WhatsApp integration (MOCKED)
- In-app **Quick Add** page mirrors the exact message format the Twilio webhook will accept.
- `webhook_server.py` — FastAPI stub with `/whatsapp/inbound` endpoint. Not started by supervisor. Go-live requires `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` and a public URL, then wire the Twilio Sandbox to it.
- Users link their WhatsApp number in Settings → WhatsApp.

### Categories
- 5 defaults per new user (Food / Drinks / Stationery / Outing / Miscellaneous).
- **Add categories** from Settings **or** inline via the "＋ New category" expander on the Expenses page.
- Delete custom categories.

### Settings
- Name, currency (INR/USD/EUR/GBP/JPY/AUD/CAD), theme (light/dark), default starting balance.
- WhatsApp number.
- JSON export (all your data) + CSV export of expenses.
- JSON import (restore).
- Reset my data (two-step confirm).

### Design
- Two themes:
  - **Light** — warm ivory `#F2F2ED` + deep burgundy `#8F002B`.
  - **Dark** — deep navy `#0E1220` + burgundy accents.
- Custom typography: Fraunces (display) + Manrope (body).
- Mobile-first responsive; cards stack vertically at ≤640 px; no horizontal scroll.

---

## 3. Business rules (the invariants)

These are the rules the app **must** obey. Break any of them and finances get wrong.

1. **Balance is derived, never stored.**  
   `Available Balance = starting_balance + Σ(balance_additions) + Σ(borrowed_received) + Σ(friend_repaid) − Σ(expenses) − Σ(borrowed_repaid)`
2. **Borrowed money is NOT income.** It increases the wallet and creates a debt; it must be excluded from spending analytics that answer "how much did I really earn?".
3. **Money a friend owes is NOT part of available balance** until they actually pay.
4. **Negative balance is allowed.** Show it clearly with `⚠️`, do not block further expenses.
5. **Every finance row is user-scoped** by `user_id`. All service functions require `user_id` as the first argument.
6. **OCR results are never saved silently.** Users must confirm before an expense affects the balance.
7. **Recurring rules use `last_run`** to be idempotent — running twice in a day never double-posts.

---

## 4. Tech stack

- Python 3.11
- Streamlit 1.40
- SQLite (embedded, single file at `data/finance.db`)
- Pandas 2.3 + Plotly 5.24 for analytics + charts
- Pillow 11 + pytesseract 0.3 for OCR (needs system `tesseract-ocr`)
- bcrypt 4.2 + PyJWT 2.10 for auth
- FastAPI (only in `webhook_server.py`, not required for the Streamlit app to run)

---

## 5. Project structure

```
app.py                  # entry point — auth gate, sidebar, page dispatch
webhook_server.py       # FastAPI stub for Twilio WhatsApp (MOCKED)

database/
    database.py         # SQLite schema, get_conn(), get_setting(), init_db()
pages_app/
    auth.py             # sign in / create account screens
    dashboard.py        # hero balance + stats + quick actions
    expenses.py         # add / add-balance / OCR / history (+ inline "New category")
    quick_add.py        # WhatsApp-style chat
    borrow_lend.py      # borrows + lents + confirm dialogs
    recurring.py        # recurring-expense rules
    reports.py          # metrics, donut, bar, monthly trend, savings tips
    budget.py           # total + per-category budgets w/ progress bars
    settings.py         # profile, categories, whatsapp, export/import, danger
services/
    auth_service.py     # bcrypt + JWT, user CRUD
    balance_service.py  # available_balance(), month_summary(), add_balance()
    expense_service.py  # expenses + categories + debts + budgets
    analytics_service.py# month_report(), compare_last_months(), budget_progress()
    recommendation_service.py # rule-based savings tips
    recurring_service.py# add_rule(), run_due(), list_rules(), toggle_rule()
    ocr_service.py      # Tesseract extraction
    quickadd_service.py # NL parser used by Quick Add + Twilio webhook
    demo_service.py     # seed demo data for a new user
components/
    theme.py            # CSS + palettes (light + dark)
    cards.py            # hero balance, stat card, tx card, empty state
    charts.py           # Plotly donut / bar / line
utils/
    constants.py        # DEFAULT_CATEGORIES, TX_ types, BALANCE_SOURCES, CURRENCIES
    formatting.py       # format_money, format_date, month_label, greeting

assets/                 # icons / images (empty by default)
data/                   # runtime — SQLite file lives here (auto-created)

requirements.txt
packages.txt            # tesseract-ocr (for Streamlit Cloud)
.streamlit/config.toml
.env.example
README.md
PROJECT_HANDOFF.md      # this file
CONTINUE_PROJECT_PROMPT.txt
```

---

## 6. Database schema

All finance tables carry a `user_id` foreign key to `users`.

- **users** — id, email (unique), password_hash (bcrypt), name, whatsapp_number
- **categories** — user_id, name, icon, color  `UNIQUE(user_id, name)`
- **expenses** — user_id, amount, category, description, date, merchant, source (`manual` / `screenshot` / `quickadd` / `recurring`), screenshot_path
- **balance_transactions** — user_id, amount, tx_type (`balance_addition` / `borrowed_received` / `borrowed_repaid` / `friend_repaid`), source, description, date, related_debt_id
- **debts** — user_id, direction (`borrowed` / `lent`), person, amount, reason, date, status (`open` / `settled`), settled_date
- **budgets** — user_id, year, month, category (`TOTAL` or category name), amount
- **recurring_expenses** — user_id, amount, category, description, frequency (`monthly` / `weekly`), day_of_month, day_of_week, start_date, end_date, last_run, active
- **whatsapp_messages** — user_id, direction (`in` / `out`), body, parsed_amount, parsed_category, expense_id, status
- **app_settings** — user_id, key, value  `UNIQUE(user_id, key)`

---

## 7. Running locally

```bash
# system
sudo apt-get install -y tesseract-ocr       # Debian/Ubuntu
brew install tesseract                      # macOS

# python
pip install -r requirements.txt

# run
streamlit run app.py
```

Open `http://localhost:8501`. On first launch the `demo@example.com` account is created and seeded automatically.

### Optional `.env`
```
JWT_SECRET=<hex-string>       # otherwise auto-generated & cached in data/.jwt_secret
TESSERACT_CMD=/usr/bin/tesseract   # only if not on PATH
TWILIO_ACCOUNT_SID=…          # only needed for live WhatsApp
TWILIO_AUTH_TOKEN=…
```

---

## 8. Deploying

### Streamlit Community Cloud
- Push repo to GitHub.
- `packages.txt` (already in root) installs `tesseract-ocr`.
- App file: `app.py`.

### Replit
- Import the repo.
- Run command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`.
- Add `tesseract-ocr` under `replit.nix` if not present.

### Emergent
- Existing preview pod runs `streamlit run app.py` on port 3000 via supervisor (see `/etc/supervisor/conf.d/streamlit.conf`).
- Persist `data/` if you want SQLite to survive pod rebuilds.

### Twilio WhatsApp (go-live)
1. Join the free Twilio WhatsApp Sandbox.
2. Set `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` env vars.
3. Run `python webhook_server.py` on a public host (port 8002).
4. Point the Sandbox webhook to `<host>:8002/whatsapp/inbound`.
5. Users paste their WhatsApp number in Settings → WhatsApp.

---

## 9. Testing status

- **Iteration 1** (pre-auth): 100% pass, 8/8 balance-math cases + 1 E2E.
- **Iteration 2** (auth + isolation + recurring + quick-add): **100% pass, 12/12 flows**. Auth gate, register, per-user isolation, quick-add valid + invalid, recurring create/post/pause/delete, WhatsApp UI, change-password round-trip, sign-out, negative-balance.

Test credentials — see `memory/test_credentials.md` (in-repo before packaging).

---

## 10. Known limitations & backlog

- Live Twilio WhatsApp receiving is **MOCKED** — code is wired, credentials are not.
- No password-reset by email yet (change-password requires the current password).
- Streamlit `st.tabs` doesn't support programmatic tab activation, so dashboard quick-actions land on the target page's default tab (Expenses → Add Expense).
- Single-tenant SQLite: for teams, migrate to Postgres and adjust the get_conn() helper.

### Ideas for the next iteration
- Password reset via email (SendGrid / Resend).
- Family / shared-wallet mode.
- LLM-generated savings narrative (Emergent LLM key).
- Currency conversion on symbol switch.
- Mobile bottom-nav FAB.

---

## 11. Files-of-interest cheat sheet

| Question | File |
| --- | --- |
| How is available balance computed? | `services/balance_service.py::available_balance` |
| Where do expenses get inserted? | `services/expense_service.py::add_expense` |
| How does borrow flow affect balance? | `services/expense_service.py::add_debt` + `settle_debt` |
| How is OCR performed? | `services/ocr_service.py::extract_from_image` |
| How is the message "Lunch 180 Food" parsed? | `services/quickadd_service.py::parse` |
| How do recurring rules auto-post? | `services/recurring_service.py::run_due` + `app.py::_recurring_ran_this_session` |
| Where is auth? | `services/auth_service.py`, `pages_app/auth.py` |
| Theme + CSS? | `components/theme.py` |
| Schema? | `database/database.py::SCHEMA` |

If in doubt, the invariants in section 3 are what the code enforces.

# Personal Finance (Streamlit) — PRD

## Vision
A polished, mobile-first personal money command center. Track balance, expenses, borrows/lends, monthly reports, budgets, and get rule-based savings recommendations. Now multi-user with **JWT auth**, **recurring expenses**, and a **WhatsApp-style Quick Add** (with a mocked Twilio webhook ready for later go-live).

## Tech stack
Python 3.11 · Streamlit 1.40 · SQLite · Plotly · Pillow · Tesseract OCR (pytesseract) · bcrypt · PyJWT · FastAPI (webhook stub only).

## Core requirements (static)
1. SQLite persistence, single source of truth. Balance derived from transactions.
2. Multi-user with fully isolated data (user_id foreign key on every finance table).
3. JWT-based auth (email + password, bcrypt). Session state in Streamlit.
4. Borrowed money increases balance; money friends owe does NOT until received.
5. Negative balance allowed with clear warning; user never blocked.
6. Payment-screenshot OCR extracts amount / merchant / date / suggested category; user confirms before saving.
7. Quick Add: natural-language parser (`Lunch 180 Food` → expense) usable in-app and via a WhatsApp webhook stub.
8. Recurring expenses auto-post on due dates (checked once per session).
9. Mobile-first responsive layout, no horizontal scroll.
10. Currency selectable (INR default). Light (ivory + burgundy) and dark (navy + burgundy) themes.

## Implemented (2026-09-06)
### Foundations
- Modular architecture — `app.py`, `database/`, `services/`, `pages_app/`, `components/`, `utils/`.
- SQLite schema: users, categories, expenses, balance_transactions, debts, budgets, recurring_expenses, app_settings, whatsapp_messages — every finance row has `user_id`.

### Auth & user state (new)
- `services/auth_service.py`: bcrypt hashing, JWT token issue/verify, register / login / change_password / update_profile / get_user_by_whatsapp.
- `pages_app/auth.py`: sign-in and create-account tabs on unauthenticated visit.
- Sidebar shows user name/email and a Sign Out button.
- Auto-created demo user `demo@example.com / demo123` seeded with 10 expenses, +₹500 balance, one borrow, one lent so first-time visitors see a live-looking app.

### Recurring expenses (new)
- `services/recurring_service.py`: monthly / weekly rules with day-of-month or day-of-week, optional end date; `run_due(user_id)` posts all missed instances and updates `last_run`.
- `pages_app/recurring.py`: create rule, pause/activate, delete, or manually "Post any due now".
- Auto-posts once per session on any page load.

### Quick Add + WhatsApp (new)
- `services/quickadd_service.py`: natural-language parser (`"Lunch 180 Food"`, `"₹250 Drinks Coffee with mom"`).
- `pages_app/quick_add.py`: WhatsApp-style chat UI with bubbles, message log persisted in `whatsapp_messages` table. Accepts text or receipt photo (OCR).
- `webhook_server.py`: FastAPI stub for Twilio inbound webhook — **MOCKED**. Ready to point at Twilio Sandbox by adding `TWILIO_ACCOUNT_SID/AUTH_TOKEN` and running the FastAPI process. Users link their number in Settings → WhatsApp.

### Everything else (from MVP)
- Dashboard: hero balance card, 4 stat cards, 4 quick-action buttons (Add Expense / Add Balance / Borrow-Lend / Quick Add), category donut, recent transactions.
- Expenses: Add / Add Balance / Scan Screenshot (Tesseract) / History with filter, sort, search, edit & delete.
- Borrow & Lend: three tabs, confirm dialogs before repay/receive, balance math verified.
- Reports: metrics, donut, horizontal bar, monthly-trend line, MoM comparison narrative, rule-based savings tips.
- Budget & Goals: total + per-category budgets, progress bars, over-budget warnings.
- Settings: profile, WhatsApp number, categories CRUD, JSON+CSV export/import, change password, danger reset.

## Testing status
- **Iteration 1** (pre-auth): 100% pass, 8/8 balance-math + 1 full E2E flow.
- **Iteration 2** (auth + isolation + recurring + quick-add): **100% pass, 12/12 flows**. Auth gate, register, per-user isolation, quick-add valid+invalid, recurring create+post+pause+delete, Settings WhatsApp UI, change-password round-trip, sign-out, negative-balance behaviour — all verified.

## Backlog / P1
- Real Twilio WhatsApp go-live (already wired — just needs credentials & public URL).
- Password reset via email (Resend / SendGrid integration).
- Mobile: bottom-nav FAB with persistent Add-Expense.
- Cloud sync / Google Drive backup.

## P2 ideas
- LLM-generated savings narrative (Emergent LLM key).
- Family / shared-wallet mode with per-user sub-accounts.
- Currency conversion when switching primary currency.
- SMS-based add via Twilio SMS as an alt to WhatsApp.

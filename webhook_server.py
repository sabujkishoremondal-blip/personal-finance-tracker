"""Twilio WhatsApp webhook stub — MOCKED.

Run separately (e.g. `python webhook_server.py`) and point Twilio Sandbox to
`http://<host>:8002/whatsapp/inbound`. On receipt of a message we:

1. Look up the sender's `whatsapp_number` in our users table.
2. Parse the text via `services.quickadd_service.parse`.
3. Create an expense and log the exchange.
4. Reply with a TwiML `<Response><Message>...`.

This file is intentionally decoupled from Streamlit so it can be deployed
alongside or on a separate host. Twilio credentials are only needed to send
outbound replies through the Twilio REST API — inbound webhooks require no
credentials from us (Twilio just POSTs), but you should verify the request
signature in production (`twilio.request_validator.RequestValidator`).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, Form, Response  # noqa: E402
from services.auth_service import get_user_by_whatsapp  # noqa: E402
from services.quickadd_service import parse, confirm_and_save  # noqa: E402
from services.balance_service import available_balance  # noqa: E402
from database.database import get_conn, init_db  # noqa: E402

init_db()
app = FastAPI(title="Personal Finance — WhatsApp Webhook")


def _twiml(reply: str) -> Response:
    body = f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{reply}</Message></Response>"
    return Response(content=body, media_type="application/xml")


def _log(user_id: int, direction: str, body: str, expense_id=None, status="saved",
         parsed_amount=None, parsed_category=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO whatsapp_messages(user_id,direction,body,parsed_amount,"
            "parsed_category,expense_id,status) VALUES(?,?,?,?,?,?,?)",
            (user_id, direction, body, parsed_amount, parsed_category, expense_id, status),
        )


@app.get("/health")
def health():
    return {"status": "ok",
            "twilio_configured": bool(os.environ.get("TWILIO_ACCOUNT_SID"))}


@app.post("/whatsapp/inbound")
def inbound(From: str = Form(...), Body: str = Form(""), NumMedia: int = Form(0)):
    """Twilio posts application/x-www-form-urlencoded with fields:
       From (e.g. 'whatsapp:+919876543210'), Body, NumMedia, MediaUrl0, MediaContentType0…
    """
    sender = From.replace("whatsapp:", "").strip()
    user = get_user_by_whatsapp(sender)
    if not user:
        return _twiml(
            f"👋 Welcome! This number isn't linked to any account. "
            f"Open the app → Settings → WhatsApp and save {sender} to your profile."
        )
    _log(user["id"], "in", Body or "[media]")
    if not Body:
        return _twiml("Please send text like: 'Lunch 180 Food'. (Photo OCR coming soon.)")
    parsed = parse(user["id"], Body)
    if not parsed["ok"]:
        reply = parsed["error"] or "Couldn't understand that."
        _log(user["id"], "out", reply, status="failed")
        return _twiml(reply)
    eid = confirm_and_save(user["id"], parsed)
    bal = available_balance(user["id"])
    reply = (f"✅ {parsed['category']} · ₹{parsed['amount']:.0f}"
             f"{' — ' + parsed['description'] if parsed['description'] else ''}\n"
             f"Balance: ₹{bal:.0f}")
    _log(user["id"], "out", reply,
         parsed_amount=parsed["amount"], parsed_category=parsed["category"],
         expense_id=eid, status="saved")
    return _twiml(reply)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_server:app",
                host="0.0.0.0", port=int(os.environ.get("WEBHOOK_PORT", "8002")),
                reload=False)

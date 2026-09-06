"""In-app WhatsApp-style Quick Add.

Users type or upload a screenshot in a chat-style interface;
the parsed expense is created immediately in their account.
The same parser powers the (future) Twilio WhatsApp webhook.
"""
import io
import streamlit as st
from datetime import date
from PIL import Image
from services import quickadd_service, ocr_service
from services.expense_service import add_expense
from services.balance_service import available_balance
from database.database import get_setting, get_conn
from utils.formatting import format_money


def _uid():
    return st.session_state["user_id"]


def _log_message(uid: int, direction: str, body: str,
                 parsed_amount=None, parsed_category=None,
                 expense_id=None, status: str = "saved"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO whatsapp_messages(user_id,direction,body,parsed_amount,"
            "parsed_category,expense_id,status) VALUES(?,?,?,?,?,?,?)",
            (uid, direction, body, parsed_amount, parsed_category, expense_id, status),
        )


def _fetch_messages(uid: int, limit: int = 30) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM whatsapp_messages WHERE user_id=? "
            "ORDER BY id DESC LIMIT ?",
            (uid, limit),
        ).fetchall()
    return list(reversed([dict(r) for r in rows]))


def render():
    uid = _uid()
    currency = get_setting(uid, "currency", "INR")

    st.markdown("<h1 style='margin-bottom:0'>💬 Quick Add</h1>", unsafe_allow_html=True)
    st.caption("Type an expense the way you'd tell a friend — or drop a receipt photo. "
               "Same input format your (future) WhatsApp bot will accept.")

    _inject_chat_css()

    st.markdown('<div class="chat-window">', unsafe_allow_html=True)
    msgs = _fetch_messages(uid)
    if not msgs:
        st.markdown(
            '<div class="chat-empty">'
            'Try typing:  <b>“Lunch 180 Food”</b>  or  <b>“₹250 Drinks Coffee with mom”</b>'
            '</div>',
            unsafe_allow_html=True,
        )
    for m in msgs:
        _bubble(m, currency)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # Input
    tab_text, tab_photo = st.tabs(["✍️ Text", "📷 Photo"])

    with tab_text:
        with st.form("qa_text_form", clear_on_submit=True):
            text = st.text_input(
                "Message",
                placeholder="e.g. Coffee 60 Drinks",
                label_visibility="collapsed",
                key="qa_text_input",
            )
            send = st.form_submit_button("Send", use_container_width=True)
            if send and text.strip():
                _handle_text(uid, text.strip())
                st.rerun()

    with tab_photo:
        up = st.file_uploader("Send a receipt photo",
                              type=["png", "jpg", "jpeg", "webp"], key="qa_photo")
        if up and st.button("Send photo", use_container_width=True):
            _handle_photo(uid, up.getvalue())
            st.rerun()

    st.markdown(
        "<div style='margin-top:16px;text-align:center;color:var(--muted);font-size:12px;'>"
        "Balance: <b>" + format_money(available_balance(uid), currency) + "</b>"
        "</div>",
        unsafe_allow_html=True,
    )


def _handle_text(uid: int, text: str):
    _log_message(uid, "in", text)
    parsed = quickadd_service.parse(uid, text)
    if not parsed["ok"]:
        reply = parsed["error"] or "Couldn't understand that. Try 'Lunch 180 Food'."
        _log_message(uid, "out", reply, status="failed")
        return
    eid = quickadd_service.confirm_and_save(uid, parsed)
    bal = available_balance(uid)
    reply = (f"✅ Added {parsed['category']} · ₹{parsed['amount']:.0f}"
             f"{' — ' + parsed['description'] if parsed['description'] else ''}\n"
             f"Balance: ₹{bal:.0f}")
    _log_message(uid, "out", reply,
                 parsed_amount=parsed["amount"],
                 parsed_category=parsed["category"],
                 expense_id=eid, status="saved")


def _handle_photo(uid: int, data: bytes):
    _log_message(uid, "in", "[receipt photo]")
    if not ocr_service.is_available():
        _log_message(uid, "out",
                     "OCR unavailable on server. Please type the expense.",
                     status="failed")
        return
    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        _log_message(uid, "out", "Couldn't read the image.", status="failed")
        return
    result = ocr_service.extract_from_image(img)
    if not result["ok"] or not result["amount"]:
        _log_message(uid, "out",
                     "I couldn't confidently read the amount. "
                     "Please retry with a clearer photo or type the expense.",
                     status="needs_review")
        return
    eid = add_expense(uid, result["amount"], result["category"],
                      (result["merchant"] or "Receipt")[:60],
                      d=result["date"] or date.today(),
                      merchant=result["merchant"] or "",
                      source="quickadd")
    bal = available_balance(uid)
    reply = (f"📷 Read receipt: {result['category']} · ₹{result['amount']:.0f}"
             f"{' from ' + result['merchant'] if result['merchant'] else ''}\n"
             f"Saved. Balance: ₹{bal:.0f}")
    _log_message(uid, "out", reply,
                 parsed_amount=result["amount"],
                 parsed_category=result["category"],
                 expense_id=eid, status="saved")


def _bubble(m: dict, currency: str):
    if m["direction"] == "in":
        side = "in"
    else:
        side = "out"
    # multiline safe
    body = (m["body"] or "").replace("\n", "<br/>")
    st.markdown(
        f'<div class="chat-row {side}"><div class="bubble {side}">{body}</div></div>',
        unsafe_allow_html=True,
    )


def _inject_chat_css():
    st.markdown(
        """
    <style>
    .chat-window {
        background: var(--surface2); border:1px solid var(--border);
        border-radius:20px; padding:16px; min-height:280px; max-height:520px;
        overflow-y:auto; display:flex; flex-direction:column; gap:8px;
    }
    .chat-empty {
        text-align:center; color:var(--muted); padding:40px 12px;
        font-size:14px;
    }
    .chat-row { display:flex; }
    .chat-row.in  { justify-content:flex-end; }
    .chat-row.out { justify-content:flex-start; }
    .bubble {
        max-width:78%; padding:10px 14px; border-radius:16px;
        font-size:14px; line-height:1.45; white-space:pre-wrap;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .bubble.in {
        background: var(--primary); color:#fff !important;
        border-bottom-right-radius:6px;
    }
    .bubble.in * { color:#fff !important; }
    .bubble.out {
        background: var(--surface); color:var(--text) !important;
        border:1px solid var(--border); border-bottom-left-radius:6px;
    }
    @media (max-width: 640px) {
        .bubble { max-width: 88%; }
    }
    </style>
        """,
        unsafe_allow_html=True,
    )

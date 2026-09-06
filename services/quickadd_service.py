"""Natural-language quick-add parser used by:
- In-app 'Quick Add' chat (WhatsApp-style)
- Twilio WhatsApp webhook (future, in /app/webhook_server.py)

Grammar accepted (order-insensitive):
    <amount> <category> <description...>
    Examples:
        180 Food Lunch at canteen
        Coffee 60 Drinks
        Rs. 250 Outing movie
        ₹1200 Rent

Returns:
    {'amount': float, 'category': str, 'description': str, 'ok': bool, 'error': str}
"""
import re
from typing import Optional
from services.expense_service import list_categories


AMOUNT_RE = re.compile(
    r"(?:₹|Rs\.?|INR|\$|USD)?\s*(\d+(?:[.,]\d{1,2})?)",
    re.IGNORECASE,
)


def parse(user_id: int, text: str) -> dict:
    result = {"amount": None, "category": None,
              "description": "", "ok": False, "error": ""}
    if not text or not text.strip():
        result["error"] = "Empty message."
        return result

    # Find amount (largest reasonable number)
    tokens = text.split()
    amount_val = None
    amount_token_idx = None
    for i, tok in enumerate(tokens):
        m = AMOUNT_RE.fullmatch(tok.strip(",."))
        if m:
            try:
                v = float(m.group(1).replace(",", "."))
                if 0 < v <= 1_000_000:
                    if amount_val is None or v > amount_val:
                        amount_val = v
                        amount_token_idx = i
            except ValueError:
                pass
    if amount_val is None:
        result["error"] = "No amount found. Try: 'Lunch 180 Food' or '250 Drinks Coffee'."
        return result
    result["amount"] = amount_val

    # Find category — match any known category name in the message
    cats = [c["name"] for c in list_categories(user_id)]
    matched_cat_idx = None
    text_lower = text.lower()
    for cat in cats:
        # word-boundary match, case-insensitive
        m = re.search(rf"\b{re.escape(cat.lower())}\b", text_lower)
        if m:
            result["category"] = cat
            # find token index that begins near match
            for i, tok in enumerate(tokens):
                if tok.lower().strip(",.") == cat.lower():
                    matched_cat_idx = i
                    break
            break
    if not result["category"]:
        result["category"] = "Miscellaneous"

    # Description = the rest
    remove = set()
    if amount_token_idx is not None:
        remove.add(amount_token_idx)
    if matched_cat_idx is not None:
        remove.add(matched_cat_idx)
    desc_tokens = [t for i, t in enumerate(tokens) if i not in remove]
    # drop currency symbols left behind
    desc_tokens = [t for t in desc_tokens if t.strip(",.").lower() not in
                   {"rs", "rs.", "inr", "₹", "$", "usd"}]
    result["description"] = " ".join(desc_tokens).strip()[:100]
    result["ok"] = True
    return result


def confirm_and_save(user_id: int, parsed: dict, d=None) -> Optional[int]:
    """Create expense from a successfully parsed message."""
    if not parsed.get("ok"):
        return None
    from services.expense_service import add_expense
    return add_expense(user_id, parsed["amount"], parsed["category"],
                       parsed["description"] or parsed["category"],
                       d=d, source="quickadd")

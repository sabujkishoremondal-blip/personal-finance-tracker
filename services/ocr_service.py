"""Tesseract-based OCR for UPI/payment screenshots.

Best-effort extraction of amount, merchant/person, date and category.
If confidence is low the caller MUST let the user confirm/edit.
"""
import os
import re
from datetime import datetime, date
from typing import Optional
from PIL import Image

try:
    import pytesseract
    _TESS_CMD = os.environ.get("TESSERACT_CMD")
    if _TESS_CMD:
        pytesseract.pytesseract.tesseract_cmd = _TESS_CMD
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False


AMOUNT_RE = re.compile(
    r"(?:₹|Rs\.?|INR|\$|USD|EUR|€|£)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
    re.IGNORECASE,
)
AMOUNT_FALLBACK_RE = re.compile(r"\b([0-9]{2,7}(?:\.[0-9]{1,2})?)\b")
DATE_RES = [
    re.compile(r"(\d{1,2})[-/\s](\d{1,2})[-/\s](\d{2,4})"),
    re.compile(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{2,4})"),
    re.compile(r"([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{2,4})"),
]
MONTHS = {m.lower(): i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
MONTHS_FULL = {m.lower(): i for i, m in enumerate(
    ["January","February","March","April","May","June","July","August",
     "September","October","November","December"], 1)}

CATEGORY_HINTS = {
    "Food": ["restaurant","cafe","kitchen","dhaba","biryani","food","zomato",
             "swiggy","mcdonald","pizza","kfc","hotel","dining","meal","lunch",
             "dinner","breakfast"],
    "Drinks": ["starbucks","chai","tea","coffee","beverage","juice","cafe"],
    "Stationery": ["stationery","books","xerox","print","pen","notebook"],
    "Outing": ["movie","pvr","inox","bookmyshow","travel","uber","ola",
               "cab","metro","bus","train","irctc","ticket","park","zoo"],
    "Miscellaneous": [],
}


def is_available() -> bool:
    return _AVAILABLE


def _parse_date(text: str) -> Optional[date]:
    text = text.replace("Sept", "Sep")
    for r in DATE_RES:
        for m in r.finditer(text):
            g = m.groups()
            try:
                if g[1].isalpha():
                    day = int(g[0])
                    mon = MONTHS_FULL.get(g[1].lower()) or MONTHS.get(g[1][:3].lower())
                    year = int(g[2])
                    if year < 100:
                        year += 2000
                    if mon:
                        return date(year, mon, day)
                elif g[0].isalpha():
                    mon = MONTHS_FULL.get(g[0].lower()) or MONTHS.get(g[0][:3].lower())
                    day = int(g[1])
                    year = int(g[2])
                    if year < 100:
                        year += 2000
                    if mon:
                        return date(year, mon, day)
                else:
                    day, mon, year = int(g[0]), int(g[1]), int(g[2])
                    if year < 100:
                        year += 2000
                    if 1 <= mon <= 12 and 1 <= day <= 31:
                        return date(year, mon, day)
            except Exception:
                continue
    return None


def _parse_amount(text: str) -> Optional[float]:
    m = AMOUNT_RE.search(text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except Exception:
            pass
    # fallback: pick the largest plausible number
    candidates = []
    for m in AMOUNT_FALLBACK_RE.finditer(text):
        try:
            v = float(m.group(1).replace(",", ""))
            if 1 <= v <= 1_000_000:
                candidates.append(v)
        except Exception:
            pass
    return max(candidates) if candidates else None


def _guess_merchant(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    stop = ("paid", "received", "sent", "successful", "transaction", "utr",
            "ref", "upi", "bank", "amount", "date", "time")
    for ln in lines:
        low = ln.lower()
        if any(low.startswith(s) or s in low[:12] for s in stop):
            continue
        if re.search(r"[A-Za-z]{3,}", ln) and len(ln) < 60:
            # skip pure numbers
            if re.match(r"^[\d\s.,:/-]+$", ln):
                continue
            return ln[:60]
    return ""


def _guess_category(text: str) -> str:
    low = text.lower()
    for cat, kws in CATEGORY_HINTS.items():
        if any(kw in low for kw in kws):
            return cat
    return "Miscellaneous"


def extract_from_image(img: Image.Image) -> dict:
    """Return dict with amount, merchant, date, category, raw_text, ok."""
    result = {
        "amount": None, "merchant": "", "date": None,
        "category": "Miscellaneous", "raw_text": "", "ok": False,
        "error": "",
    }
    if not _AVAILABLE:
        result["error"] = "Tesseract OCR not installed on server."
        return result
    try:
        # Preprocess: grayscale for better accuracy
        gray = img.convert("L")
        text = pytesseract.image_to_string(gray)
    except Exception as e:
        result["error"] = f"OCR failed: {e}"
        return result

    result["raw_text"] = text
    result["amount"] = _parse_amount(text)
    result["date"] = _parse_date(text) or datetime.now().date()
    result["merchant"] = _guess_merchant(text)
    result["category"] = _guess_category(text)
    result["ok"] = result["amount"] is not None
    return result

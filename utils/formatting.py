from datetime import datetime
from utils.constants import CURRENCIES


def get_symbol(currency: str = "INR") -> str:
    return CURRENCIES.get(currency, "₹")


def format_money(amount: float, currency: str = "INR", show_sign: bool = False) -> str:
    sym = get_symbol(currency)
    sign = ""
    if show_sign and amount > 0:
        sign = "+"
    elif amount < 0:
        sign = "-"
    val = abs(amount)
    # Indian style grouping for INR
    if currency == "INR":
        s = f"{val:,.0f}" if val == int(val) else f"{val:,.2f}"
        # convert to lakhs formatting only if large; keep standard comma for simplicity
        return f"{sign}{sym}{s}"
    s = f"{val:,.2f}" if val != int(val) else f"{val:,.0f}"
    return f"{sign}{sym}{s}"


def format_date(dt) -> str:
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    return dt.strftime("%d %b %Y")


def month_label(year: int, month: int) -> str:
    return datetime(year, month, 1).strftime("%B %Y")


def greeting() -> str:
    h = datetime.now().hour
    if h < 12:
        return "Good morning"
    if h < 17:
        return "Good afternoon"
    return "Good evening"

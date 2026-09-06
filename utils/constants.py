DEFAULT_CATEGORIES = [
    {"name": "Food",          "icon": "🍔", "color": "#8F002B"},
    {"name": "Drinks",        "icon": "🥤", "color": "#B23A5A"},
    {"name": "Stationery",    "icon": "📚", "color": "#6F0022"},
    {"name": "Outing",        "icon": "🎉", "color": "#D0778D"},
    {"name": "Miscellaneous", "icon": "📦", "color": "#58001B"},
]

BALANCE_SOURCES = ["Pocket Money", "Salary", "Family", "Refund", "Gift", "Other"]

TX_EXPENSE            = "expense"
TX_BALANCE_ADD        = "balance_addition"
TX_BORROW_RECEIVED    = "borrowed_received"
TX_BORROW_REPAID      = "borrowed_repaid"
TX_FRIEND_RECEIVED    = "friend_repaid"   # friend paid us back
# friend_owed does NOT affect available balance until received

CURRENCIES = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "AUD": "A$",
    "CAD": "C$",
}

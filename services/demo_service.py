"""Seed demo data for a fresh install."""
from datetime import date, timedelta
from database.database import get_conn, set_setting


def seed_demo_data():
    with get_conn() as conn:
        n = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        if n > 0:
            return
    set_setting("starting_balance", "2000")

    today = date.today()
    first = today.replace(day=1)

    def d(offset_from_first: int) -> str:
        return (first + timedelta(days=offset_from_first)).isoformat()

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO balance_transactions(amount,tx_type,source,description,date) "
            "VALUES(?,?,?,?,?)",
            (500, "balance_addition", "Pocket Money", "Weekly allowance", d(2)),
        )
        sample_expenses = [
            (180, "Food",          "Lunch at college",     d(0),  "College Canteen"),
            (240, "Food",          "Dinner takeaway",      d(1),  "Zomato"),
            (95,  "Drinks",        "Coffee catch-up",      d(2),  "Starbucks"),
            (60,  "Drinks",        "Tea break",            d(2),  "Chai Point"),
            (150, "Stationery",    "Printouts + pens",     d(3),  "Local shop"),
            (420, "Outing",        "Movie night",          d(3),  "PVR Cinemas"),
            (380, "Outing",        "Dinner with friends",  d(4),  "Cafe Delight"),
            (75,  "Miscellaneous", "Auto ride",            d(4),  "Ola"),
            (220, "Food",          "Groceries",            d(5),  "More"),
            (130, "Drinks",        "Smoothie",             d(5),  "Fruit Bar"),
        ]
        for amt, cat, desc, dt, merch in sample_expenses:
            conn.execute(
                "INSERT INTO expenses(amount,category,description,date,merchant,source) "
                "VALUES(?,?,?,?,?, 'manual')",
                (amt, cat, desc, dt, merch),
            )

        cur = conn.execute(
            "INSERT INTO debts(direction,person,amount,reason,date) "
            "VALUES('borrowed','Rahul',500,'Emergency',?)",
            (d(4),),
        )
        did = cur.lastrowid
        conn.execute(
            "INSERT INTO balance_transactions(amount,tx_type,source,description,date,related_debt_id) "
            "VALUES(500,'borrowed_received','Rahul','Emergency',?,?)",
            (d(4), did),
        )
        conn.execute(
            "INSERT INTO debts(direction,person,amount,reason,date) "
            "VALUES('lent','Priya',400,'Dinner',?)",
            (d(5),),
        )

    set_setting("onboarded", "1")

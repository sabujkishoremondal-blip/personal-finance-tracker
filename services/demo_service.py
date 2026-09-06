"""Demo data seed for a newly-registered demo/main user."""
from datetime import date, timedelta
from database.database import get_conn, set_setting


def seed_demo_data(user_id: int):
    with get_conn() as conn:
        n = conn.execute("SELECT COUNT(*) FROM expenses WHERE user_id=?",
                         (user_id,)).fetchone()[0]
        if n > 0:
            return
    set_setting(user_id, "starting_balance", "2000")

    today = date.today()
    first = today.replace(day=1)

    def d(offset: int) -> str:
        return (first + timedelta(days=offset)).isoformat()

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO balance_transactions(user_id,amount,tx_type,source,description,date) "
            "VALUES(?,?,?,?,?,?)",
            (user_id, 500, "balance_addition", "Pocket Money", "Weekly allowance", d(2)),
        )
        rows = [
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
        for amt, cat, desc, dt, merch in rows:
            conn.execute(
                "INSERT INTO expenses(user_id,amount,category,description,date,merchant,source) "
                "VALUES(?,?,?,?,?,?, 'manual')",
                (user_id, amt, cat, desc, dt, merch),
            )
        cur = conn.execute(
            "INSERT INTO debts(user_id,direction,person,amount,reason,date) "
            "VALUES(?, 'borrowed','Rahul',500,'Emergency',?)",
            (user_id, d(4)),
        )
        did = cur.lastrowid
        conn.execute(
            "INSERT INTO balance_transactions(user_id,amount,tx_type,source,description,date,related_debt_id) "
            "VALUES(?,500,'borrowed_received','Rahul','Emergency',?,?)",
            (user_id, d(4), did),
        )
        conn.execute(
            "INSERT INTO debts(user_id,direction,person,amount,reason,date) "
            "VALUES(?, 'lent','Priya',400,'Dinner',?)",
            (user_id, d(5)),
        )

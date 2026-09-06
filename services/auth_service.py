"""JWT + bcrypt auth for the Streamlit app.

- Users stored in SQLite `users` table.
- Session is kept in st.session_state (no cookies) for the Streamlit UI.
- JWT tokens are issued so an external WhatsApp webhook can authenticate a
  user's number to their user_id.
"""
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from database.database import get_conn, seed_user_defaults

JWT_ALGO = "HS256"
ACCESS_TTL_MIN = 60 * 24 * 7  # 7 days for a personal finance app


def _secret() -> str:
    # ensure a persistent secret exists — generate & cache in data folder if missing
    secret = os.environ.get("JWT_SECRET")
    if secret:
        return secret
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "data" / ".jwt_secret"
    if p.exists():
        return p.read_text().strip()
    s = secrets.token_hex(32)
    p.parent.mkdir(exist_ok=True)
    p.write_text(s)
    return s


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TTL_MIN),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGO)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, _secret(), algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email=?", (email.lower().strip(),)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_whatsapp(number: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE whatsapp_number=? AND whatsapp_number != ''",
            (number.strip(),),
        ).fetchone()
        return dict(row) if row else None


def register_user(email: str, password: str, name: str = "") -> tuple[Optional[dict], Optional[str]]:
    email = email.lower().strip()
    if not email or "@" not in email:
        return None, "Please enter a valid email address."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if get_user_by_email(email):
        return None, "An account with this email already exists."
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users(email,password_hash,name) VALUES(?,?,?)",
            (email, hash_password(password), name.strip() or email.split("@")[0]),
        )
        user_id = cur.lastrowid
    seed_user_defaults(user_id, name=name.strip() or email.split("@")[0])
    return get_user_by_id(user_id), None


def login(email: str, password: str) -> tuple[Optional[dict], Optional[str]]:
    user = get_user_by_email(email)
    if not user:
        return None, "Invalid email or password."
    if not verify_password(password, user["password_hash"]):
        return None, "Invalid email or password."
    return user, None


def change_password(user_id: int, old_password: str, new_password: str) -> Optional[str]:
    user = get_user_by_id(user_id)
    if not user or not verify_password(old_password, user["password_hash"]):
        return "Current password is incorrect."
    if len(new_password) < 6:
        return "New password must be at least 6 characters."
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (hash_password(new_password), user_id),
        )
    return None


def update_profile(user_id: int, name: str = None, whatsapp_number: str = None):
    fields, vals = [], []
    if name is not None:
        fields.append("name=?")
        vals.append(name.strip())
    if whatsapp_number is not None:
        fields.append("whatsapp_number=?")
        vals.append(whatsapp_number.strip())
    if not fields:
        return
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {','.join(fields)} WHERE id=?",
                     (*vals, user_id))

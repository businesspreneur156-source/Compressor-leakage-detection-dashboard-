"""Layer 5 - Login aur roles.

Password kabhi plain text me save nahi hote. Har user ke liye
ek random salt + PBKDF2 hash save hota hai (users.json me).
Login par wahi hash dobara banake milaya jaata hai.

Roles:
    admin  - dashboard + download + stats, sab kuch
    viewer - sirf dashboard dekh sakta hai, download nahi

users.json kahan se aayega?
    1. users.json (asli file, .gitignore me hai - GitHub par nahi jayegi)
    2. warna users.json.example (demo ke liye, taaki pehli baar bhi login ho)

Demo users (sirf demo ke liye - submission se pehle badal dena):
    admin  / admin123
    viewer / viewer123
Apne user banane ke liye: python layer5/create_user.py
"""
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
USERS_FILE = HERE / "users.json"
USERS_EXAMPLE = HERE / "users.json.example"


def hash_password(password, salt=None):
    """Return (salt_hex, hash_hex). PBKDF2, 100,000 rounds, stdlib only."""
    if salt is None:
        salt = os.urandom(16)
    elif isinstance(salt, str):
        salt = bytes.fromhex(salt)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex(), hashed.hex()


def verify_password(password, salt_hex, hash_hex):
    _, hashed = hash_password(password, salt_hex)
    return hmac.compare_digest(hashed, hash_hex)


def load_users():
    for path in (USERS_FILE, USERS_EXAMPLE):
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {u["username"]: u for u in data.get("users", [])}
    return {}


def authenticate(username, password):
    """Return role ('admin'/'viewer') on success, else None."""
    users = load_users()
    user = users.get(username)
    if not user:
        return None
    if verify_password(password, user["salt"], user["hash"]):
        return user.get("role", "viewer")
    return None


def save_user(username, password, role):
    """Add/update a user in users.json (real file, not example)."""
    if role not in ("admin", "viewer"):
        raise ValueError("role admin ya viewer hona chahiye")
    salt, hashed = hash_password(password)
    users = []
    if USERS_FILE.exists():
        users = json.loads(USERS_FILE.read_text(encoding="utf-8")).get("users", [])
    users = [u for u in users if u["username"] != username]
    users.append(
        {"username": username, "salt": salt, "hash": hashed, "role": role}
    )
    USERS_FILE.write_text(json.dumps({"users": users}, indent=2), encoding="utf-8")
    return str(USERS_FILE)


if __name__ == "__main__":
    # Self-test, bina koi file banaye:
    salt, hashed = hash_password("test123")
    assert verify_password("test123", salt, hashed) is True
    assert verify_password("galat", salt, hashed) is False
    print("Auth self-test PASSED. Demo users file se check karo:")
    print(" admin role:", authenticate("admin", "admin123"))
    print(" viewer role:", authenticate("viewer", "viewer123"))
    print(" galat password:", authenticate("admin", "galat"))

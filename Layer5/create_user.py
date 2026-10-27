"""Layer 5 - Naya user banao (password terminal me chhupa ke manga jaata hai).

Run: python layer5/create_user.py
Phir username, role (admin/viewer) aur password daalo.
Ye users.json me save hoga - ye file GitHub par nahi jayegi (.gitignore).
"""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auth import save_user  # noqa: E402

if __name__ == "__main__":
    username = input("Username: ").strip()
    role = input("Role (admin/viewer): ").strip().lower()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Password dobara: ")
    if password != confirm:
        print("❌ Password match nahi hua.")
        raise SystemExit(1)
    if not username or not password:
        print("❌ Username/password khaali nahi ho sakta.")
        raise SystemExit(1)
    print("Saved:", save_user(username, password, role))
    print(f"User '{username}' ({role}) taiyaar hai. Ab dashboard_login.py me login karo.")

"""Creates the initial accounts: the 6 MIS staff plus one admin account.

Run once against a fresh database:
    ./.venv/bin/python scripts/seed_users.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import models  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.security import hash_password  # noqa: E402

STAFF = ["Marco", "Ramon", "Renz", "Erick", "Albert", "Dss"]
ADMIN = {"username": "joshua", "display_name": "Joshua Galvan"}
DEFAULT_PASSWORD = "123qwe"  # set per the team's own preference; change via the app once live


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created = []
    try:
        for display_name in STAFF:
            username = display_name.lower()
            if db.query(models.User).filter(models.User.username == username).first():
                continue
            db.add(
                models.User(
                    username=username,
                    display_name=display_name.upper(),
                    password_hash=hash_password(DEFAULT_PASSWORD),
                    is_admin=False,
                )
            )
            created.append((username, DEFAULT_PASSWORD))

        if not db.query(models.User).filter(models.User.username == ADMIN["username"]).first():
            db.add(
                models.User(
                    username=ADMIN["username"],
                    display_name=ADMIN["display_name"],
                    password_hash=hash_password(DEFAULT_PASSWORD),
                    is_admin=True,
                )
            )
            created.append((ADMIN["username"], DEFAULT_PASSWORD))

        db.commit()
    finally:
        db.close()

    if not created:
        print("All accounts already exist; nothing to do.")
        return

    print("Created accounts (share these temporary passwords privately, once):")
    print(f"{'username':<10} password")
    for username, password in created:
        print(f"{username:<10} {password}")


if __name__ == "__main__":
    main()

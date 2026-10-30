"""
Make a new admin password hash for MURYA.

Run on your own computer (not on the server):
    python make_admin_hash.py

It asks for a password (nothing is shown or saved) and prints two lines.
Paste those two lines into your Streamlit secrets (App settings > Secrets), then redeploy:

    ADMIN_PW_SALT = "..."
    ADMIN_PW_HASH = "..."

The app then uses these instead of the values written in app.py.
After that works, delete PW_SALT and PW_HASH from app.py so they are not in your public repo.
Use a long passphrase (14 characters or more), for example four unrelated words.
"""
import getpass, hashlib, os, sys

ITERATIONS = 200_000   # must match ADMIN_PW_ITER (default 200000) in the app

pw = getpass.getpass("New admin password: ")
if len(pw) < 12:
    print("That is short. Use 14 or more characters (a passphrase is best).")
    if input("Continue anyway? (y/N) ").strip().lower() != "y":
        sys.exit(1)
if getpass.getpass("Type it again: ") != pw:
    print("The two passwords did not match.")
    sys.exit(1)

salt = os.urandom(16)
digest = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITERATIONS).hex()
print()
print(f'ADMIN_PW_SALT = "{salt.hex()}"')
print(f'ADMIN_PW_HASH = "{digest}"')
print()
print("Keep the password itself somewhere safe. It cannot be recovered from the hash.")

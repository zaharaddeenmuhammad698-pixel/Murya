"""
Make the three secret values the MURYA USSD service needs.

How to run (in VS Code: Terminal > New Terminal, in the folder where this file is):
    pip install flask          (only the first time)
    python make_ussd_secrets.py

It asks for the dashboard password (nothing appears on screen as you type, that is normal),
then prints three lines. Copy each one into your host's Environment page (name on the left of the =, value on the right).
Do not put quotes around the values. Do not save them in your code or on GitHub.
"""
import getpass
import secrets
import sys

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    print("Please run this first:  pip install flask")
    sys.exit(1)

print("Choose a long password for the dashboard: 14 or more characters, for example four unrelated words.")
pw = getpass.getpass("Dashboard password: ")
if len(pw) < 12:
    print("That is too short. Run the script again and use at least 12 characters.")
    sys.exit(1)
if getpass.getpass("Type it again: ") != pw:
    print("The two passwords did not match. Run the script again.")
    sys.exit(1)

print()
print("Copy these three lines into the Environment page:")
print()
print("ADMIN_PASSWORD_HASH=" + generate_password_hash(pw))
print("USSD_TOKEN=" + secrets.token_urlsafe(32))
print("SECRET_KEY=" + secrets.token_urlsafe(48))
print()
print("Your dashboard user name is: admin")
print("Keep your password somewhere safe. It cannot be recovered from the hash.")
print("Your Africa's Talking callback URL will be: https://YOUR-APP-ADDRESS/murya/ + the USSD_TOKEN value")

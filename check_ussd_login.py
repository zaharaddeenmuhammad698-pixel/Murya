"""
Check, on your own computer, whether your dashboard password matches the ADMIN_PASSWORD_HASH you put on the server.
It tells you which of these is wrong: the hash was cut short or damaged, the password is different, or a small typing slip.

How to run (VS Code: Terminal > New Terminal, in the folder that holds this file):
    pip install flask        (only the first time)
    python check_ussd_login.py

1. Open your host's Environment page, reveal the value of ADMIN_PASSWORD_HASH and copy ONLY the value (after the = sign).
2. Paste it when asked. (You can paste with a long-press, or Ctrl+V on a laptop.)
3. Type the password you use on the sign-in page. Nothing shows as you type.
4. Read the answer. If it says there is a problem, press Enter at the first question to make a brand-new hash here, test it,
   and paste the new line into the Environment page.
"""
import getpass
import re
import secrets
import sys

try:
    from werkzeug.security import check_password_hash, generate_password_hash
except ImportError:
    print("Please run this first:  pip install flask")
    sys.exit(1)

DIGEST_HEX = {"scrypt": 128, "pbkdf2:sha256": 64, "pbkdf2:sha512": 128, "pbkdf2:sha1": 40}

def check_shape(h):
    """Return a list of plain-English problems with the hash text itself."""
    m = re.fullmatch(r"(scrypt|pbkdf2:sha\d+)(:[\d:]+)?\$([^$\s]+)\$([0-9a-f]+)", h)
    if not m:
        return ["It does not look like a hash. It must be ONE line like  scrypt:32768:8:1$salt$longnumber  with no spaces."]
    method, _, salt, digest = m.groups()
    want = DIGEST_HEX.get(method)
    if want and len(digest) != want:
        return [f"The last part is {len(digest)} characters long but should be {want}. The hash was CUT SHORT (or has extra characters) when it was copied."]
    return []

def make_new():
    print("\nMaking a new dashboard password. Use 14 or more characters, for example four unrelated words.")
    pw = getpass.getpass("New password (nothing shows as you type): ")
    if len(pw) < 12:
        print("That is too short. Run the script again."); sys.exit(1)
    if getpass.getpass("Type it again: ") != pw:
        print("The two did not match. Run the script again."); sys.exit(1)
    h = generate_password_hash(pw)
    assert check_password_hash(h, pw) and not check_shape(h)
    print("\nTested here: this hash matches the password you just typed.")
    print("\nPaste this whole line into the Environment page (name on the left, value on the right, no quote marks):\n")
    print("ADMIN_PASSWORD_HASH=" + h)
    print("\nThen wait for the server to redeploy, open /dashboard, and sign in with user name  admin  and your new password.")
    sys.exit(0)

print("Paste the value of ADMIN_PASSWORD_HASH (only the part after the = sign), then press Enter.")
print("Or just press Enter with nothing to make a NEW hash here.")
h = input("> ").strip()
if not h:
    make_new()
cleaned = h.strip('"').strip("'").strip()
if cleaned != h:
    print("Note: there were quote marks or spaces around it. The sign-in page ignores those, so that is fine.")
h = cleaned
problems = check_shape(h)
for p in problems:
    print("PROBLEM:", p)
if problems:
    print("\nFix: press Enter at the first question next time to make a fresh hash, then paste the whole new value.")
    sys.exit(1)

pw = getpass.getpass("Type the password you use on the sign-in page (nothing shows as you type): ")
if check_password_hash(h, pw):
    print("\nMATCH: this hash belongs to that password. If sign-in still fails on the server, the server is using a different value:")
    print("  - the Environment page may still hold an older hash, or the server has not redeployed since you changed it;")
    print("  - or the user name is not 'admin' (check ADMIN_USER on the Environment page).")
    sys.exit(0)

print("\nNO MATCH. Trying common slips:")
found = False
variants = {
    "the same password without a space at the end or start": pw.strip(),
    "the first letter changed to a capital letter": pw[:1].upper() + pw[1:],
    "the first letter changed to a small letter": pw[:1].lower() + pw[1:],
}
for label, v in variants.items():
    if v != pw and check_password_hash(h, v):
        print(f"  It matches {label}. Type it that way on the sign-in page.")
        found = True
if not found:
    print("  No simple slip fits. The password you typed now is not the one used to make this hash,")
    print("  or the hash on the server is an older one from an earlier try.")
    print("\nFix: run this script again, press Enter at the first question, and make a new hash. Test it here, then paste it into the Environment page.")
sys.exit(1)

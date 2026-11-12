"""
Make the page menu follow the chosen language, and make the app start at the menu page every time. Edits YOUR OWN app.py only.

What changes:
  1. The menu labels are translated: Hausa, English (and Fulfulde once approved), like the rest of the app.
  2. Changing the language keeps you on the same page. Each language gets its own menu widget, and the chosen page is put into the widget
     before it is drawn, so the menu never starts again from the first item.
  3. A new visit always opens on Home (the menu page). The page is no longer written into the web address, so a reload or a
     reconnect starts at the menu. A link with ?page=Ask still opens that page once (handy for testing); the language stays in the address.

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_nav_language_fix.py            (fixes app.py in this folder)
    python apply_nav_language_fix.py path\\to\\app.py

It saves a backup first (app.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
All or nothing: if a spot is not found, nothing is changed.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "_nav_labels" in text:
    print("Your file already has the translated menu. Nothing was changed.")
    sys.exit(0)

NAV = '''# The page menu follows the chosen language. Each language has its own widget key, and the chosen page is put into the widget
# (through session state) BEFORE it is drawn, so changing the language keeps you on the same page.
def _nav_labels():
    return [tx("nav_" + p_.replace(" ", "_")) for p_ in PAGES]
def _nav_changed():
    labels = _nav_labels()
    picked = st.session_state.get("nav_w_" + st.session_state.get("lang_choice", "Hausa"))
    if picked in labels: st.session_state.nav = PAGES[labels.index(picked)]
if st.session_state.nav not in PAGES: st.session_state.nav = "Home"
_nav_key = "nav_w_" + st.session_state.get("lang_choice", "Hausa")
_labels = _nav_labels()
st.session_state[_nav_key] = _labels[PAGES.index(st.session_state.nav)]
st.radio("Navigation", _labels, key=_nav_key, on_change=_nav_changed, horizontal=True, label_visibility="collapsed")
page = st.session_state.nav
'''
problems = []
text, n1 = re.subn(r"def _nav_changed\(\):[^\n]*\n(?:.*\n)*?page = st\.session_state\.nav\n", lambda m: NAV, text, count=1)
if not n1: problems.append("the menu block")

URL_OLD = ('try:\n    if st.query_params.get("page") != page: st.query_params["page"] = page\n'
           '    _l = st.session_state.get("lang_choice", "Hausa")\n'
           '    if st.query_params.get("lang") != _l: st.query_params["lang"] = _l\nexcept Exception: pass\n')
URL_NEW = ('try:\n    if "page" in st.query_params: del st.query_params["page"]   # a new visit starts at the menu page; a ?page= link works once\n'
           '    _l = st.session_state.get("lang_choice", "Hausa")\n'
           '    if st.query_params.get("lang") != _l: st.query_params["lang"] = _l\nexcept Exception: pass\n')
if text.count(URL_OLD) == 1: text = text.replace(URL_OLD, URL_NEW)
else: problems.append("the web-address block")

if problems:
    print("Nothing was changed. These parts were not found:", ", ".join(problems))
    print("Your file looks different from what I expected. Send me the lines around st.radio(\"Navigation\" and I will adjust the fix.")
    sys.exit(1)
try:
    compile(text, path, "exec")
except SyntaxError as e:
    print("Stopped: the result would not be valid Python (line", e.lineno, "). Your file was NOT changed.")
    sys.exit(1)

shutil.copyfile(path, path + ".bak")
out = text.replace("\n", "\r\n") if crlf else text
with open(path, "wb") as f:
    f.write(out.encode("utf-8"))
print("Done. Backup saved as", path + ".bak")
print("Commit app.py and redeploy. The menu now follows the language, and every new visit opens on Home.")

"""
Apply the language-redirect fix to YOUR OWN app.py. Nothing else in your file is touched.

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_language_fix.py            (fixes app.py in this folder)
    python apply_language_fix.py path\\to\\app.py

It makes a backup first (app.py.bak), changes three small spots, checks that the result is valid Python,
and only then saves. It keeps your line endings. If a spot is not found it says so and skips it.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")
done, skipped = [], []

def sub(name, pattern, replacement, flags=0):
    global text
    new, n = re.subn(pattern, replacement, text, count=1, flags=flags)
    if n:
        text = new; done.append(name)
    else:
        skipped.append(name)

# 1. Navigation menu: fixed labels, no "index", page placed in the widget before it is drawn.
sub("1. navigation menu",
    r'st\.radio\("Navigation", PAGES, index=PAGES\.index\(st\.session_state\.nav\), key="nav_w", on_change=_nav_changed,\s*'
    r'horizontal=True, label_visibility="collapsed", format_func=lambda p_: tx\("nav_" \+ p_\.replace\(" ", "_"\)\)\)',
    lambda m: (
        '# The menu keeps the same identity in every language (fixed labels, no "index"), so a language change cannot reset it to Home.\n'
        'def _nav_label(p_):\n'
        '    ha, en, _ = UI["nav_" + p_.replace(" ", "_")]\n'
        '    return en if ha == en else f"{ha} · {en}"\n'
        'if st.session_state.get("nav_w") != st.session_state.nav: st.session_state["nav_w"] = st.session_state.nav\n'
        'st.radio("Navigation", PAGES, key="nav_w", on_change=_nav_changed,\n'
        '         horizontal=True, label_visibility="collapsed", format_func=_nav_label)'))

# 2. Question box: the example text moves out of the box so a language change cannot clear what was typed.
sub("2. question box",
    r'(?P<ind>[ \t]*)ph = tx\("ph"\)\n(?P=ind)st\.text_area\("Tambayarka", placeholder=ph,',
    lambda m: f'{m.group("ind")}st.caption("✏️ " + tx("ph"))\n{m.group("ind")}st.text_area("Tambayarka", placeholder="…",')

# 3. Troubleshooting aid: open the app with ?debug=1 to see the session code (optional).
sub("3a. session start time",
    r'"login_msg": "", "sid": uuid\.uuid4\(\)\.hex\[:8\], "consent": False\}',
    lambda m: '"login_msg": "", "sid": uuid.uuid4().hex[:8], "consent": False, "started": datetime.now().strftime("%H:%M:%S")}')
if "3a. session start time" in done and "debug · session" not in text:
    sub("3b. debug line in the footer",
        r'(\{tx\("foot_l2"\)\}</div>\n"""\, unsafe_allow_html=True\))',
        lambda m: m.group(1) + (
            '\ntry:\n'
            '    if st.query_params.get("debug") == "1":\n'
            '        st.caption(f"debug · session {SID} · started {st.session_state.get(\'started\', \'?\')} · page {page} · language {st.session_state.get(\'lang_choice\')}")\n'
            'except Exception:\n'
            '    pass'))

if not any(d.startswith(("1", "2")) for d in done):
    print("Nothing was changed. Spots not found:", ", ".join(skipped))
    print("Your file may already have the fix, or it looks different from what I expected. Send me the lines around st.radio(\"Navigation\"...).")
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
print("Changed:", ", ".join(done))
if skipped: print("Not found, skipped:", ", ".join(skipped))

"""
Fix the "colour contrast" accessibility warning in YOUR OWN app.py. Nothing else in your file is touched.

It darkens the small grey text that is too faint for the 4.5:1 contrast rule: the message timestamps and the small
helper lines (captions). Colours used are #3f5247 on light backgrounds (contrast 7.3 to 8.4 on every background in the app).

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_contrast_fix.py            (fixes app.py in this folder)
    python apply_contrast_fix.py path\\to\\app.py

It saves a backup first (app.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "contrast fixes (WCAG AA)" in text:
    print("Your file already has the contrast fix. Nothing was changed.")
    sys.exit(0)

CSS = (
    "\n/* contrast fixes (WCAG AA): small grey text darkened to at least 7:1 */\n"
    ".bm{color:#3f5247 !important;}\n"
    '[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *{color:#3f5247 !important;opacity:1 !important;}\n'
)
new_text, n = re.subn(r"(\.stat \.n\{font-size:26px;\})", lambda m: m.group(1) + CSS.rstrip("\n"), text, count=1)
if not n:
    print("Nothing was changed: I could not find the line '.stat .n{font-size:26px;}' in your style block.")
    print("Send me the lines that start with '.stat .n' and I will adjust the fix.")
    sys.exit(1)

try:
    compile(new_text, path, "exec")
except SyntaxError as e:
    print("Stopped: the result would not be valid Python (line", e.lineno, "). Your file was NOT changed.")
    sys.exit(1)

shutil.copyfile(path, path + ".bak")
out = new_text.replace("\n", "\r\n") if crlf else new_text
with open(path, "wb") as f:
    f.write(out.encode("utf-8"))
print("Done. Backup saved as", path + ".bak")
print("Commit app.py, redeploy, then run PageSpeed again and compare the Accessibility score.")

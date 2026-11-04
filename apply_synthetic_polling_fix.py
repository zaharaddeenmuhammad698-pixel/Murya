"""
Let the polling-unit finder in YOUR OWN app.py work with SYNTHETIC data and say so loudly. Nothing else in your file is touched.

The programme asks teams to use synthetic polling-unit data, not INEC's real list. A made-up list must never look real to a voter,
so this fix adds:
  1. In Admin > Polling units: a tick box "This list is SYNTHETIC". You can import a synthetic list without INEC's permission box.
  2. On the Polling Units page: a strong banner (Hausa and English), whenever the list is marked synthetic:
     "SAMPLE DATA: these polling units are made up ... do not use them to find your real polling unit."
  3. In Admin: the status line says SYNTHETIC.

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_synthetic_polling_fix.py            (fixes app.py in this folder)
    python apply_synthetic_polling_fix.py path\\to\\app.py

It saves a backup first (app.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
All or nothing: if any spot is not found, nothing is changed.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "pu_synth" in text:
    print("Your file already has the synthetic-data label. Nothing was changed.")
    sys.exit(0)

problems = []

def once(pattern, repl, name, flags=0):
    global text
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n: text = new
    else: problems.append(name)

# 1. the banner text, in the translation table (Hausa, English, Fulfulde falls back to Hausa)
once(r'^( *)"pu_mode": \(',
     lambda m: (m.group(1) + '"pu_synth": ("⚠️ BAYANAN MISALI NE: waɗannan rumfunan zabe an ƙirƙire su ne don nuna yadda manhajar ke aiki. Ba na gaske ba ne. '
                'Kada ka yi amfani da su don neman rumfarka ta gaske. Ka duba katin zabe ko ka tambayi INEC.",\n'
                + m.group(1) + '             "⚠️ SAMPLE DATA: these polling units are made up to show how the app works. They are not real. '
                'Do not use them to find your real polling unit. Check your PVC or ask INEC.", None),\n'
                + m.group(1) + '"pu_mode": ('),
     "banner text", re.M)

# 2. the Polling Units page
once(r'( *)banner = tx\("pu_conf" if conf_pu else "pu_prov", src=esc\(src_pu\), asof=esc\(asof\)\)\n'
     r' *st\.markdown\(f\'<div class="\{"bf" if conf_pu else "bf prov"\}">\{banner\}</div>\', unsafe_allow_html=True\)',
     lambda m: (m.group(1) + 'if pu_meta("synthetic") == "1":\n'
                + m.group(1) + '    st.markdown(f\'<div class="bf prov" style="border:2px solid #b45309;"><b>{tx("pu_synth")}</b></div>\', unsafe_allow_html=True)\n'
                + m.group(1) + 'else:\n'
                + m.group(1) + '    banner = tx("pu_conf" if conf_pu else "pu_prov", src=esc(src_pu), asof=esc(asof))\n'
                + m.group(1) + '    st.markdown(f\'<div class="{"bf" if conf_pu else "bf prov"}">{banner}</div>\', unsafe_allow_html=True)'),
     "Polling Units page banner")

# 3. Admin > Polling units
once(r'( *)perm = st\.checkbox\("I have INEC\'s written permission to use this list", key="pu_perm"\)',
     lambda m: (m.group(0) + '\n' + m.group(1) + 'synth_in = st.checkbox("This list is SYNTHETIC (made up for demonstration, not real polling units)", '
                'value=pu_meta("synthetic") == "1", key="pu_synth_in")'),
     "synthetic tick box")
once(r'if not perm: st\.warning\("Tick the permission box first\."\)',
     'if not (perm or synth_in): st.warning("Tick the permission box, or tick that the list is synthetic.")',
     "import permission check")
once(r'pu_set_meta\("source", src_in\.strip\(\)\); pu_set_meta\("confirmed", "0"\)',
     'pu_set_meta("source", src_in.strip()); pu_set_meta("confirmed", "0"); pu_set_meta("synthetic", "1" if synth_in else "0")',
     "import saves the flag")
once(r'pu_set_meta\("confirmed", "1" if conf_in else "0"\); st\.rerun\(\)',
     'pu_set_meta("confirmed", "1" if conf_in else "0"); pu_set_meta("synthetic", "1" if synth_in else "0"); st.rerun()',
     "save button saves the flag")
once(r'\+ \("CONFIRMED by INEC" if pu_meta\("confirmed"\) == "1" else "awaiting INEC confirmation"\)\)',
     '+ ("SYNTHETIC (demonstration data)" if pu_meta("synthetic") == "1" else "CONFIRMED by INEC" if pu_meta("confirmed") == "1" else "awaiting INEC confirmation"))',
     "Admin status line")

if problems:
    print("Nothing was changed. These parts were not found in your file:", ", ".join(problems))
    print("Your file looks different from what I expected. Send me those parts and I will adjust the fix.")
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
print("Commit app.py and redeploy. In Admin > Polling units, tick 'This list is SYNTHETIC', choose your CSV and press Import.")

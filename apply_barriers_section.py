"""
Add the organisers' SYNTHETIC accessibility-barriers survey to the Dashboard page of YOUR OWN app.py. Nothing else is touched.

What you get, at the bottom of the Dashboard page:
    - a strong "SYNTHETIC SAMPLE" banner (Hausa and English),
    - filters for LGA (or state, for the organisers' file) and for language (Hausa, Fulfulde, English...),
    - a bar chart of the main barrier people named, and three figures,
    - a table that says how MURYA responds to each barrier (built, partly, or not covered).

MURYA itself collects no disability data. This section only READS the organisers' made-up file.

Put a survey file in a folder called data next to app.py. It uses the first one it finds:
    data/accessibility_barriers_survey_synthetic_bauchi.csv   (made for MURYA: 20 Bauchi LGAs, Hausa/Fulfulde/English;
                                                               make it with make_synthetic_barriers_bauchi.py)
    data/accessibility_barriers_survey_synthetic.csv          (the organisers' file: 20 states, six languages)
If there is no file, the Dashboard shows a short note instead.
Running the script again UPGRADES an earlier version of this section.

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_barriers_section.py            (fixes app.py in this folder)
    python apply_barriers_section.py path\\to\\app.py

It saves a backup first (app.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
"""
import re
import shutil
import sys

# --- THIS IS THE BLOCK WEY MISS BEFORE ---
BLOCK = r'''
        # --- Accessibility barriers v2 ---
        def _barriers_section():
            import os
            import csv
            from collections import Counter
            st.markdown("---")
            st.markdown("### ♿ Accessibility Barriers - SYNTHETIC SAMPLE")
            st.warning("⚠️ SYNTHETIC SAMPLE - Ba ainihin bayanai ba / NOT REAL DATA - This is made-up sample data from organisers. MURYA collects NO disability data.")
            # Find file
            p1 = os.path.join("data", "accessibility_barriers_survey_synthetic_bauchi.csv")
            p2 = os.path.join("data", "accessibility_barriers_survey_synthetic.csv")
            fpath = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)
            if not fpath:
                st.info("No synthetic survey file found. Put file in data/ folder to see chart.")
                return
            try:
                rows = list(csv.DictReader(open(fpath, encoding="utf-8")))
            except Exception as e:
                st.info(f"Could not read survey file: {e}")
                return
            if not rows:
                st.info("Survey file is empty.")
                return
            # Columns - try to be flexible
            cols = rows[0].keys()
            lga_col = "lga" if "lga" in cols else ("state" if "state" in cols else list(cols)[0])
            lang_col = "language" if "language" in cols else None
            barrier_col = "barrier" if "barrier" in cols else ("main_barrier" if "main_barrier" in cols else list(cols)[-1])
            # Filters
            lgas = sorted(set(str(r.get(lga_col, "")).strip() for r in rows if r.get(lga_col)))
            sel_lga = st.selectbox("Filter by LGA / State", ["All"] + lgas, key="barriers_lga")
            if lang_col:
                langs = sorted(set(str(r.get(lang_col, "")).strip() for r in rows if r.get(lang_col)))
                sel_lang = st.selectbox("Filter by Language", ["All"] + langs, key="barriers_lang")
            else:
                sel_lang = "All"
            filtered = rows
            if sel_lga != "All":
                filtered = [r for r in filtered if str(r.get(lga_col, "")).strip() == sel_lga]
            if sel_lang != "All" and lang_col:
                filtered = [r for r in filtered if str(r.get(lang_col, "")).strip() == sel_lang]
            c1, c2, c3 = st.columns(3)
            c1.metric("Responses (Synthetic)", len(filtered))
            c2.metric("LGAs / States", len(set(str(r.get(lga_col, "")) for r in filtered)))
            c3.metric("Languages", len(set(str(r.get(lang_col, "")) for r in filtered)) if lang_col else 0)
            counts = Counter(str(r.get(barrier_col, "")).strip() for r in filtered if r.get(barrier_col))
            if counts:
                st.bar_chart(counts)
            st.markdown("#### How MURYA Responds")
            st.table({
                "Barrier": ["No internet / Data cost", "Cannot read English", "No voice / Cannot see well", "No trust in info"],
                "MURYA Response": ["Built - Lightweight, WhatsApp share", "Built - Hausa / Fulfulde / English", "Partly - Voice input/output, large text", "Built - Human-approved, INEC source shown"],
                "Status": ["✅ Built", "✅ Built", "🟡 Partly", "✅ Built"]
            })
        _barriers_section()
'''

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "barriers v2" in text:
    print("Your file already has the latest barriers section. Nothing was changed.")
    sys.exit(0)

upgrade = "def _barriers_section" in text
if upgrade:
    pattern = r"\n    # --- Accessibility barriers[^\n]*\n    def _barriers_section\(\):\n(?:.*\n)*?    _barriers_section\(\)\n"
    new_text, n = re.subn(pattern, lambda m: BLOCK, text, count=1)
    what = "Upgraded the barriers section."
else:
    pattern = (r"(        for r in pub:\n"
               r"            st\.markdown\(f'<div class=\"bu\">\{esc\(r\[\"q\"\]\)\}</div><div class=\"ba\"><div class=\"who\">✅ MURYA</div>\{esc\(r\[\"a\"\]\)\}</div>', unsafe_allow_html=True\)\n)")
    new_text, n = re.subn(pattern, lambda m: m.group(1) + BLOCK, text, count=1)
    what = "Added the barriers section."
if not n:
    print("Nothing was changed: I could not find the Dashboard spot to change.")
    print("Send me the last 10 lines of the Dashboard section and I will adjust the fix.")
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
print(what)
print("Put your survey file in the data folder, commit app.py, and redeploy. Look at the bottom of the Dashboard page.")
"""
Make the question matcher in YOUR OWN app.py tolerate typos and common spellings. Nothing else in your file is touched.

Why: on a held-out test of noisy questions (typos, Hausa/English mixing, voice-to-text noise, very short phrasing) the matcher scored
72%, lower than a plain word-matching baseline (81%). The failures were spelling: "colect", "chek", "ofice", "Torro",
"fotokopi", and "ofis" (the usual Hausa spelling of office).

What it changes (all or nothing):
  1. Adds common spellings to the concept lists: ofis, ofice, fotokopi.
  2. Removes "babu" from the "original card" concept ("babu" means "none", so it pulled unrelated questions to the PVC answer).
  3. Adds a small typo corrector: an unknown word that is very close to a known word (a concept word, an office word or an LGA name)
     is read as that word. Unknown words that are not close to anything are left alone.
  4. Uses the same corrector when looking for an LGA office question ("ofishin INEC a Torro").

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_noise_fix.py              (fixes app.py in this folder)
    python apply_noise_fix.py path\\to\\app.py

It saves a backup first (app.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "def _fix_word" in text:
    print("Your file already has the typo corrector. Nothing was changed.")
    sys.exit(0)

problems = []

def replace_once(t, old, new, name):
    if t.count(old) != 1:
        problems.append(name); return t
    return t.replace(old, new)

# 1-2. concept lists and office words
text = replace_once(text, '"ofishi", "ofishin", "office", "offices"', '"ofishi", "ofishin", "ofis", "ofice", "office", "offices"', "office spellings")
text = replace_once(text, '"kwafi", "kwafin"}', '"kwafi", "kwafin", "fotokopi", "fotokofi"}', "photocopy spellings")
text = replace_once(text, '"asali", "original", "genuine", "without", "babu"}', '"asali", "original", "genuine", "without"}', "'babu' concept")
text = replace_once(text, 'OFFICE_WORDS = {"ofishin", "ofishi", "office", "karbi", "collect", "dauka", "pick"}',
                    'OFFICE_WORDS = {"ofishin", "ofishi", "ofis", "ofice", "office", "karbi", "collect", "dauka", "pick"}', "OFFICE_WORDS")
text = replace_once(text, 'OFFICE_ONLY = {"ofishin", "ofishi", "office"}', 'OFFICE_ONLY = {"ofishin", "ofishi", "ofis", "ofice", "office"}', "OFFICE_ONLY")

# 3. typo corrector + mtoks
FIX = '''_LGA_WORDS = ("alkaleri", "bauchi", "bogoro", "dambam", "damban", "darazo", "dass", "gamawa", "ganjuwa", "giade", "itas", "gadau",
              "katagum", "azare", "kirfi", "misau", "ningi", "shira", "tafawa", "balewa", "bununu", "toro", "warji", "zaki", "madaki")
_FIX_CACHE = {}
def _fix_word(w):
    """Read a typo as the nearest known word (concept word, office word or LGA name). Words far from all of them are left alone."""
    if w in _FIX_CACHE: return _FIX_CACHE[w]
    out = w
    if len(w) >= 4 and not w.isdigit() and w not in STOP and w not in CONCEPT_OF and w not in OFFICE_WORDS and w not in _LGA_WORDS:
        import difflib
        near = difflib.get_close_matches(w, sorted(set(CONCEPT_OF) | OFFICE_WORDS | set(_LGA_WORDS)), n=1, cutoff=0.88 if len(w) == 4 else 0.8)
        if near: out = near[0]
    _FIX_CACHE[w] = out
    return out

def mtoks(text: str) -> set:
    out = set()
    for w in re.findall(r"[a-z0-9]+", norm(text)):
        w = _fix_word(w)
        c = CONCEPT_OF.get(w)
        if c: out.add(c); continue
        if len(w) <= 2 or w in STOP or w in GENERIC: continue
        out.add(w[:4] if len(w) >= 5 else w)
    return out

'''
text, n1 = re.subn(r'def mtoks\(text: str\) -> set:\n(?:[ \t]+[^\n]*\n|\n)*?(?=def kb_match)', lambda m: FIX, text, count=1)
if not n1: problems.append("mtoks function")

# 4. LGA office questions with the corrector
LGA = '''def lga_hit(question):
    """Return the LGA name a question is asking an office location for, else None."""
    words = [_fix_word(w) for w in re.findall(r"[a-z0-9']+", norm(question))]
    t = {w for w in words if len(w) > 2 and w not in STOP}
    if not (t & OFFICE_WORDS): return None
    q = " ".join(words)
    for name, pat in LGA_PATTERNS.items():
        if re.search(pat, q): return name
    # bare "ofishin INEC a Bauchi" -> Bauchi LGA office (Kofar Ran); "karbi PVC a Bauchi" is NOT matched
    if (t & OFFICE_ONLY) and re.search(r"\\bbauchi\\b", q):
        return "Bauchi (Kofar Ran)"
    return None

'''
text, n2 = re.subn(r'def lga_hit\(question\):\n(?:[ \t]+[^\n]*\n|\n)*?(?=MATCH_THRESHOLD)', lambda m: LGA, text, count=1)
if not n2: problems.append("lga_hit function")

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
print("Commit app.py and redeploy. Then run  python compare_retrieval.py  to see the new numbers.")

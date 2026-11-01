"""
Make MURYA's answer matching forgive typos. Edits only the matcher in YOUR OWN app.py.

Why: people mistype, and voice-to-text mishears. "yaushe zbae zai gudana" should still find the election date. This adds a
small helper that matches a mistyped word of five or more letters to the closest word the app already knows (one edit away,
or two for words of eight letters or more; swapping two neighbouring letters counts as one edit). Short words are never "corrected",
and a question that matches nothing still goes to a person.

Use (in VS Code: Terminal > New Terminal, in the folder that holds app.py):
    python apply_typo_fix.py                  (fixes app.py in this folder)
    python apply_typo_fix.py path\\to\\app.py

It saves a backup first (app.py.bak), keeps your line endings, checks the result is valid Python, and only then saves.
Then run:  python eval_retrieval.py   to see the before and after numbers.
"""
import re
import shutil
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

if "def near_word" in text:
    print("Your file already has the typo fix. Nothing was changed.")
    sys.exit(0)

NEW_MTOKS = '''def _osa(a, b, maxd):
    """Edit distance between two words (swapping two neighbouring letters counts as one edit). Returns maxd+1 if farther than maxd."""
    if abs(len(a) - len(b)) > maxd: return maxd + 1
    prev2, prev = None, list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                cur[j] = min(cur[j], prev2[j - 2] + 1)
        prev2, prev = prev, cur
    return prev[-1]

def near_word(w, vocab):
    """The closest known word for a probably mistyped word (only words of 5+ letters are ever corrected)."""
    if len(w) < 5 or w in vocab: return None
    maxd = 1 if len(w) < 8 else 2
    best, bd = None, maxd + 1
    for v in sorted(vocab):
        d = _osa(w, v, maxd)
        if d < bd: best, bd = v, d
    return best if bd <= maxd else None

def mtoks(text: str, vocab=()) -> set:
    out = set()
    for w in re.findall(r"[a-z0-9]+", norm(text)):
        if vocab and w not in CONCEPT_OF:
            fixed = near_word(w, vocab)
            if fixed: w = fixed
        c = CONCEPT_OF.get(w)
        if c: out.add(c); continue
        if len(w) <= 2 or w in STOP or w in GENERIC: continue
        out.add(w[:4] if len(w) >= 5 else w)
    return out
'''

pat_mtoks = r'def mtoks\(text: str\) -> set:\n(?:[ \t]+[^\n]*\n)+'
new_text, n1 = re.subn(pat_mtoks, lambda m: NEW_MTOKS, text, count=1)

pat_docs = r'(    docs = \[mtoks\(f"\{k\[\'q\'\]\} \{k\.get\(\'q_en\'\) or \'\'\} \{k\.get\(\'keywords\'\) or \'\'\}"\) for k in kb\]\n)'
ADD = ('    vocab = set(CONCEPT_OF) | {w for k in kb for w in re.findall(r"[a-z0-9]+", norm(f"{k[\'q\']} {k.get(\'q_en\') or \'\'} {k.get(\'keywords\') or \'\'}")) if len(w) >= 5}\n'
       '    qt = mtoks(question, vocab) or qt     # forgive typos: a mistyped word is matched to the closest word the app knows\n')
new_text, n2 = re.subn(pat_docs, lambda m: m.group(1) + ADD, new_text, count=1)

if not (n1 and n2):
    print("Nothing was changed. Not found:", ", ".join(x for x, ok in (("the mtoks function", n1), ("the docs line in kb_match", n2)) if not ok))
    print("Your matcher may look different from what I expected. Send me the lines from 'def mtoks' to the end of 'def kb_match'.")
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
print("Next: run  python eval_retrieval.py  to compare before and after.")

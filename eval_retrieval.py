"""
MURYA retrieval evaluation (Track 3 "Your turn" items 1 and 3).

Compares, on the same questions:
  A. a plain TF-IDF baseline,
  B. MURYA's own matcher (concepts + stems, taken from your app.py),
  C. (optional) a multilingual embedding model.

It tests clean questions AND the hard cases the brief asks for: typos, voice-to-text noise, code-switching (Hausa + English
in one sentence) and very short low-literacy phrasing. It also counts how often a question that should go to a human
gets a wrong answer instead (the "never invent answers" rule), and checks answer lengths for SMS / USSD.

Run (in VS Code terminal, in the folder that holds app.py):
    python eval_retrieval.py                       (A and B, no downloads)
    python eval_retrieval.py app.py --embeddings sentence-transformers/LaBSE     (adds C; needs: pip install sentence-transformers)

It writes RETRIEVAL_RESULTS.md, a table you can paste into your README. The embedding step is a comparison, not part of the app.
Check that a model supports Hausa before you rely on it; results for Hausa can be much weaker than for English.
"""
import io, math, random, re, sys, unicodedata

args = [a for a in sys.argv[1:]]
emb_model = None
if "--embeddings" in args:
    i = args.index("--embeddings"); emb_model = args[i + 1]; del args[i:i + 2]
APP = args[0] if args else "app.py"

# ---- load MURYA's pure functions straight from your app.py (no Streamlit needed) ----
src = open(APP, encoding="utf-8").read()
ns = {"re": re, "math": math, "unicodedata": unicodedata}
exec(src[src.index("# --- BEGIN PURE"):src.index("# --- END PURE")], ns)
norm, STOP, kb_match = ns["norm"], ns["STOP"], ns["kb_match"]

# ---- the knowledge base the app starts with (4 FAQs + the 20 offices), as a fresh install has it ----
kb = []
for k in ns["SEED_KB"]:
    en = ns["EN_DRAFTS"].get(k["q"], ("", ""))
    kb.append(dict(k, reviewed="x", q_en=en[0], a_en=en[1], en_reviewed="x"))
for n in ns["LGA_OFFICES"]:
    q, a = ns["lga_qa"](n)
    kb.append({"q": q, "a": a, "keywords": n, "source": ns["LGA_SRC"], "reviewed": "x"})
FAQ = kb[:len(ns["SEED_KB"])]

# ---- question sets ----
clean = [(q, e) for q, e in ns["EVAL_QA"]]
code_switch = [("Ina so in duba my PVC status", 0), ("Where zan collect PVC dina?", 2), ("Zabe 2027 date nawa ne?", 1),
               ("Can I vote da photocopy na katina?", 3), ("Ofishin INEC mafi near da ni", 2), ("Is my kati ready yet?", 0),
               ("Yaushe election din zai gudana?", 1), ("Ba ni da original card, zan iya vote?", 3), ("Check my PVC a ina?", 0),
               ("Wane date ne presidential zabe?", 1), ("Where ake bada kati?", 2)]
short_lowlit = [("kati na ya fito", 0), ("zabe yaushe", 1), ("ofis inec", 2), ("hoto na kati ya yi?", 3), ("kati asali", 3),
                ("wata zabe", 1), ("inda zan dauki kati", 2), ("duba kati", 0), ("kati ya shirya?", 0), ("zabe da waya", 3)]

rnd = random.Random(7)
def typo(q):
    words = q.split(); idx = [i for i, w in enumerate(words) if len(re.sub(r"\W", "", w)) >= 5]
    for i in rnd.sample(idx, min(2, len(idx))):
        w = words[i]
        if len(w) > 4:
            j = rnd.randint(1, len(w) - 3); w = w[:j] + w[j + 1] + w[j] + w[j + 2:]   # swap two neighbouring letters
        words[i] = w
    return " ".join(words)
def asr(q):   # speech-to-text style: no capitals or punctuation, some small words lost, a filler word in front
    w = re.sub(r"[^\w\s']", "", q.lower()).split()
    w = [x for i, x in enumerate(w) if i % 5 != 3 or len(x) > 4]
    return rnd.choice(["eh ", "to ", "wai ", ""]) + " ".join(w)
positives = [(q, e) for q, e in clean if e is not None]
typos = [(typo(q), e) for q, e in positives]
asrs = [(asr(q), e) for q, e in positives]
negatives = [(q, None) for q, e in clean if e is None]

SETS = [("Clean questions", [x for x in clean if x[1] is not None]), ("Typos", typos), ("Voice-to-text noise", asrs),
        ("Code-switching", code_switch), ("Short / low-literacy", short_lowlit)]

# ---- A. TF-IDF baseline (same information MURYA gets: question, English question, keywords) ----
def words(t): return [w for w in re.findall(r"[a-z0-9]+", norm(t)) if len(w) > 2 and w not in STOP]
docs = [words(f"{k['q']} {k.get('q_en', '')} {k.get('keywords', '')}") for k in FAQ]
N = len(docs); df = {}
for d in docs:
    for w in set(d): df[w] = df.get(w, 0) + 1
idf = {w: math.log((1 + N) / (1 + c)) + 1 for w, c in df.items()}
def vec(ws):
    v = {}
    for w in ws:
        if w in idf: v[w] = v.get(w, 0) + idf[w]
    n = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {w: x / n for w, x in v.items()}
dvecs = [vec(d) for d in docs]
def tfidf_match(q, thr=0.25):
    qv = vec(words(q))
    sims = [sum(qv.get(w, 0) * x for w, x in dv.items()) for dv in dvecs]
    b = max(range(N), key=lambda i: sims[i])
    return b if sims[b] >= thr else None

# ---- B. MURYA's matcher ----
def murya_match(q):
    m, _ = kb_match(q, kb)
    if m is None: return None
    return FAQ.index(m) if m in FAQ else "office"

matchers = {"TF-IDF baseline": tfidf_match, "MURYA matcher": murya_match}

# ---- C. optional multilingual embeddings ----
if emb_model:
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(emb_model)
        dtext = [f"{k['q']} {k.get('q_en', '')}" for k in FAQ]
        demb = model.encode(dtext, normalize_embeddings=True)
        def emb_match(q, thr=0.5):
            s = model.encode([q], normalize_embeddings=True)[0] @ demb.T
            b = int(s.argmax()); return b if s[b] >= thr else None
        matchers["Embeddings: " + emb_model.split("/")[-1]] = emb_match
    except Exception as e:
        print("Embedding comparison skipped:", type(e).__name__, str(e)[:100])

# ---- run ----
def office_question(q): return ns["lga_hit"](q) is not None
rows, neg_rows = [], []
for name, fn in matchers.items():
    r = {"Method": name}
    for sname, qs in SETS:
        ok = 0
        for q, e in qs:
            got = fn(q)
            ok += (got == e)
        r[sname] = f"{ok}/{len(qs)}"
    wrong = sum(1 for q, _ in negatives if fn(q) is not None)
    r["Wrongly answered (should go to a person)"] = f"{wrong}/{len(negatives)}"
    rows.append(r)

cols = ["Method"] + [s for s, _ in SETS] + ["Wrongly answered (should go to a person)"]
def table(rows):
    out = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    for r in rows: out += "| " + " | ".join(str(r[c]) for c in cols) + " |\n"
    return out
t = table(rows)

# ---- answer lengths for SMS (160, plain letters only) and USSD (182) ----
def gsm_ok(s): return s.isascii()
lens = []
for k in FAQ:
    for label, txt in (("Hausa", k["a"]), ("English", k.get("a_en") or "")):
        if txt: lens.append((k["id"] if "id" in k else FAQ.index(k) + 1, label, len(txt), gsm_ok(txt)))
too_long = [(i, l, n, g) for i, l, n, g in lens if n > 160]
report = t + f"\nQuestions per set: " + ", ".join(f"{s} {len(qs)}" for s, qs in SETS) + f"; should-go-to-a-person {len(negatives)}.\n"
report += f"\nAnswer length for SMS (160 characters) and USSD (182): {len(lens) - len(too_long)} of {len(lens)} FAQ answers fit; "
report += "longer ones: " + (", ".join(f"FAQ {i} {l} ({n} chars)" for i, l, n, g in too_long) or "none") + ".\n"
nonascii = [(i, l) for i, l, n, g in lens if not g]
if nonascii: report += "Answers with letters outside plain SMS text (they shrink SMS to 70 characters): " + ", ".join(f"FAQ {i} {l}" for i, l in nonascii) + ".\n"
print(report)
open("RETRIEVAL_RESULTS.md", "w", encoding="utf-8").write("# Retrieval results\n\n" + report +
    "\n*Questions written by the developer; typo and voice-noise variants were generated automatically from the clean set. "
    "A comparison on a small set, not a benchmark. Real-user accuracy is measured in the pilot.*\n")
print("Saved RETRIEVAL_RESULTS.md")

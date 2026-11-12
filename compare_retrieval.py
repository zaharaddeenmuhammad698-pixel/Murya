"""
Compare three ways of matching a question to an approved FAQ answer (Track 3 "Your turn" items 1 to 3).

    A. TF-IDF baseline      (like the organisers' starter: words only, no Hausa/English concept layer)
    B. MURYA matcher        (the matcher inside app.py: bilingual concepts, word stems, rarity weighting, abstention)
    C. Multilingual embeddings (optional; needs:  pip install sentence-transformers)

All three only RETURN approved text or hand over to a human, so none can invent an answer. What differs is how often
each one returns the right approved answer, a wrong one, or correctly hands over.

Fair test: each method's hand-over threshold is chosen on the 60-question development set from app.py, then every method is
scored on that set and on a separate noisy set (typos, Hausa/English mixing, voice-to-text noise, very short phrasing).

Run (VS Code terminal, in the folder that holds app.py):
    python compare_retrieval.py             (A and B)
    pip install sentence-transformers       (first time, about 500 MB; best in Google Colab)
    python compare_retrieval.py             (A, B and C)
"""
import math, re, sys, unicodedata

APP = sys.argv[1] if len(sys.argv) > 1 else "app.py"
src = open(APP, encoding="utf-8").read()
ns = {"re": re, "math": math, "unicodedata": unicodedata}
exec(src[src.index("# --- BEGIN PURE"):src.index("# --- END PURE")], ns)

# ---- the approved fact base, as the app builds it: 4 FAQs (with English questions) + 20 office answers ----
KB = []
for k in ns["SEED_KB"]:
    en = ns["en_draft_for"](k["q"])
    KB.append(dict(k, q_en=en[0], reviewed="seed"))
for name in ns["LGA_OFFICES"]:
    q, a = ns["lga_qa"](name)
    KB.append({"q": q, "a": a, "keywords": name, "source": ns["LGA_SRC"], "reviewed": "", "q_en": ns["en_draft_for"](q)[0]})
INDEX = {k["q"]: i for i, k in enumerate(KB)}
OFFICE = {name: INDEX[ns["lga_qa"](name)[0]] for name in ns["LGA_OFFICES"]}
def doc_text(k): return f'{k["q"]} {k.get("q_en") or ""} {k.get("keywords") or ""}'

NOISY = [
 # typos
 ("yaya zan duba katn zabe na", 0), ("Where can i colect my voter card", 2), ("wen is the elecshun in 2027", 1),
 ("Can i vote wit photocopy of card", 3), ("yaushe zabn 2027", 1), ("Ina zan karbi katina a ofshin INEC", 2),
 ("ofishin INEC a Torro", "OFFICE:Toro"), ("how do i chek my PVC statuss", 0), ("pls wher is INEC ofice in Misau", "OFFICE:Misau"),
 ("zan iya zabe da fotokopi na kati", 3),
 # code-switching (Hausa and English in one sentence)
 ("Ina so in check PVC dina", 0), ("Yaushe election din zai gudana", 1), ("Zan iya vote da photocopy?", 3),
 ("Ina zan collect katina?", 2), ("Is katin zabe na ready?", 0), ("INEC office din Dass yana ina", "OFFICE:Dass"),
 # voice-to-text noise (no punctuation, dropped words, odd order)
 ("yaya zan duba kati zabe", 0), ("yaushe zabe janairu", 1), ("ina karbi kati ofishin", 2), ("hoto kati waya zabe", 3),
 ("inda zan dauki kati na zabe bauchi", 2), ("ofishin inec toro", "OFFICE:Toro"), ("wane lokaci zabe", 1),
 ("when election gudana", 1), ("katina yana nan ko babu", 0),
 # very short, low-literacy phrasing
 ("zabe yaushe", 1), ("kati na ya fito", 0), ("ofis inec jamare", "OFFICE:Jama'are"), ("ina ofis dass", "OFFICE:Dass"),
 ("ofis inec giade", "OFFICE:Giade"),
 # should be handed to a human (no approved answer exists)
 ("asdf qwer", None), ("hello", None), ("zabe zabe zabe", None), ("Wane jam'iyya zan zaba", None),
 ("how much is data bundle", None), ("tell me about football", None), ("Ina son in koma makaranta", None),
]
def expected_doc(e):
    if e is None or isinstance(e, int): return e
    return OFFICE[e.split(":", 1)[1]]
DEV = [(q, expected_doc(e)) for q, e in ns["EVAL_QA"]]
TEST = [(q, expected_doc(e)) for q, e in NOISY]

# ---- A. TF-IDF baseline (plain words, cosine similarity) ----
def words(t): return re.findall(r"[a-z0-9']+", unicodedata.normalize("NFKD", t.lower()))
DOCS = [words(doc_text(k)) for k in KB]
DF = {}
for d in DOCS:
    for w in set(d): DF[w] = DF.get(w, 0) + 1
IDF = {w: math.log((1 + len(DOCS)) / (1 + c)) + 1 for w, c in DF.items()}
def vec(ws):
    v = {}
    for w in ws:
        if w in IDF: v[w] = v.get(w, 0) + IDF[w]
    n = math.sqrt(sum(x * x for x in v.values())) or 1
    return {w: x / n for w, x in v.items()}
DVEC = [vec(d) for d in DOCS]
def tfidf_scores(q):
    v = vec(words(q)); return [sum(x * dv.get(w, 0) for w, x in v.items()) for dv in DVEC]

def best_of(scores, thr):
    i = max(range(len(scores)), key=lambda j: scores[j])
    return i if scores[i] >= thr else None

def tune(score_fn, grid):
    """Choose the hand-over threshold on the development set only."""
    best = max(grid, key=lambda t: sum(best_of(score_fn(q), t) == e for q, e in DEV))
    return best

def report(name, predict, thr_note=""):
    out = {}
    for label, data in (("development (60)", DEV), ("noisy (held out)", TEST)):
        right = wrong = missed = 0
        for q, e in data:
            got = predict(q)
            if got == e: right += 1
            elif got is None: missed += 1          # should have answered, handed over instead
            else: wrong += 1                       # returned a different approved answer
        n = len(data); out[label] = (right, wrong, missed, n)
    return name, thr_note, out

results = []
t_tfidf = tune(tfidf_scores, [x / 100 for x in range(5, 80, 5)])
results.append(report("A. TF-IDF baseline", lambda q: best_of(tfidf_scores(q), t_tfidf), f"threshold {t_tfidf:.2f}"))

def murya_predict(q):
    m, _ = ns["kb_match"](q, KB)
    return None if m is None else INDEX.get(m["q"])
results.append(report("B. MURYA matcher", murya_predict, f"threshold {ns['MATCH_THRESHOLD']}"))

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    model = SentenceTransformer("intfloat/multilingual-e5-small")
    D = model.encode(["passage: " + doc_text(k) for k in KB], normalize_embeddings=True)
    cache = {}
    def emb_scores(q):
        if q not in cache: cache[q] = (model.encode(["query: " + q], normalize_embeddings=True)[0] @ D.T).tolist()
        return cache[q]
    t_emb = tune(emb_scores, [round(0.70 + 0.01 * i, 2) for i in range(0, 25)])
    results.append(report("C. Multilingual embeddings (e5-small)", lambda q: best_of(emb_scores(q), t_emb), f"threshold {t_emb:.2f}"))
except ImportError:
    print("(Skipping C: run  pip install sentence-transformers  to include multilingual embeddings.)\n")

print("| Method | Set | Right | Wrong approved answer | Handed to human when it should have answered |")
print("|---|---|---|---|---|")
for name, note, out in results:
    for label, (r, w, m, n) in out.items():
        print(f"| {name} ({note}) | {label} | {r}/{n} ({100*r//n}%) | {w} | {m} |")
print("\nNo method here can invent an answer: each returns approved text or hands over. 'Right' includes correctly handing over.")
print("Small, developer-written test sets: treat these as a comparison of methods, not as real-world accuracy.")

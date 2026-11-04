# MURYA evaluation

Version 1.0 · 3 November 2026 · Reproduce with `python compare_retrieval.py` (in the repository root, next to `app.py`).

## 1. What is evaluated

| Question | How it is measured |
|---|---|
| Does the matcher return the right approved answer? | Right, wrong, or correctly handed to a person, on two question sets |
| Can the system invent an answer? | By design, no: it returns approved text or hands over. A wrong approved answer is counted as an error |
| Do typos, mixed languages and voice-to-text noise break it? | A held-out noisy set |
| Is it accessible? | Lighthouse (PageSpeed Insights), plus manual checks |
| Do real users get answers faster and more correctly? | The usability test sheet |
| Is the USSD path usable on a basic phone? | Every screen is plain ASCII and within 182 characters; all 20 LGA offices reachable |
| Is sign-in secure and clear? | Automated sign-in scenarios in a test harness |

## 2. Matching methods compared

- **A. Plain TF-IDF** word matching, like the organisers' starter.
- **B. MURYA matcher:** Hausa and English concepts, word stems, rarity weighting, a typo corrector, and a hand-over rule.
- **C. Multilingual embeddings** (`intfloat/multilingual-e5-small`): the script includes this; it has not been run yet.

Each method's hand-over threshold is chosen on the development set only, then every method is scored on both sets. The questions were written by the developer, so these results compare methods; they do not measure real-world accuracy.

## 3. Results

| Method | Development (60) | Noisy held-out (37) |
|---|---|---|
| A. Plain TF-IDF (threshold 0.20) | 49/60 (81%) | 30/37 (81%) |
| B. MURYA matcher, before the typo and spelling fix | 58/60 (96%) | 27/37 (72%) |
| B. MURYA matcher, after the fix | 58/60 (96%) | 34/37 (91%) |
| C. Multilingual embeddings | *(not yet run)* | *(not yet run)* |

- The first noisy run showed the MURYA matcher losing to the baseline on spelling variants such as "colect", "ofice", "Torro", "fotokopi" and "ofis". The fix adds those spellings and reads a very close typo as the nearest known word.
- Three noisy questions still miss. An unrelated word such as "lokaci" (time) can still pull a question toward the election-date FAQ. A suggested FAQ is shown only as a "related answer" while a person replies.
- The "after" score is optimistic because the failures guided the fix.

## 4. Other checks

| Check | Result |
|---|---|
| Risk flags (link, vote-buying, rumour, flood-rumour, contact request, partisan) | 9/9 on a small hand-written set |
| USSD screens | 75 screens, plain ASCII, longest 133 characters; all 20 LGA offices reachable |
| Lighthouse (mobile, home page, 31 Oct 2026) | Accessibility 96, Best Practices 100, SEO 92, Performance 92 |
| Sign-in service | Tested for wrong password, wrong user name, capital letter, trailing spaces, quote marks around the hash, a damaged hash, a blocked cookie, lockout, reply and logout |
| Number removal | Phone-style numbers, long ID numbers and emails removed; polling-unit codes and dates left alone |

## 5. Still to measure

1. **Usability pilot:** at least 15 volunteers in 3 or more LGAs, including people who cannot read English. Two swapped question sets (usual way and MURYA). Report the right answer without help, minutes, help needed, ease and wrong answers.
2. **Speech-to-text accuracy:** record 20 short Hausa voice notes, type what each person said, and compute word error rate = (substitutions + deletions + insertions) ÷ words said. Fulfulde has no recognition and goes to a person.
3. **Embeddings comparison** (method C) on a laptop or in Google Colab.
4. **Accessibility:** Lighthouse on the other pages (`?page=Verified%20Info`, `?page=Polling%20Units`, `?page=Ask`) and a TalkBack test.
5. **Web app on 2G:** try Chrome with the network throttled to "Slow 3G" and report what happens.
6. **Native-speaker review:** named Hausa and Fulfulde reviewers, with dates.

## 6. Limits

Small, developer-written test sets, four FAQs and twenty office answers. The numbers show how the methods compare. They are not a promise of real-world accuracy, which the pilot will begin to measure.

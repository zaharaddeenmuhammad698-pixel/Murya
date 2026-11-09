# MURYA model card

AI4Elections Hackathon 2026–2027 · Track 3 · Version 1.3 (prototype)

## 1. System summary

MURYA (Muryar Zabe) is a voter-information helpdesk for Bauchi State. It is a **retrieval system with human approval**, not a text generator. It matches a citizen's question to a fact that a person has already verified, and shows the source. When it cannot match, a person answers.

**MURYA does not train or fine-tune any model.** It uses no personal data for training.

## 2. Components

| Component | What it does | Provider / method | Required? |
|---|---|---|---|
| Answer matching | Finds the closest verified fact | Our own code: Hausa and English concept matching, word stems, rarity weighting, and a typo corrector that reads a mistyped word as the nearest known word (Python `difflib`) | Yes |
| Office and polling-unit lookup | Shows an INEC office address, or the polling units in a ward | Database lookup from INEC's published office directory and a synthetic polling-unit list; no machine learning | Yes |
| Risk flags | Marks links, vote-buying, rumours (including flood-linked), phone numbers, party names | Regular-expression rules | Yes |
| Number removal | Removes phone-style numbers, long ID numbers and emails before a message is saved | Regular-expression rules | Yes |
| Speech-to-text | Turns Hausa or English voice notes into text for the reviewer | OpenAI Whisper (`whisper-1`) | Optional |
| Draft assistant | Suggests a reply from confirmed facts only; a person edits and publishes | Anthropic model (default `claude-haiku-5-5`) | Optional |
| Listen buttons | English: server voice (Google gTTS), or the phone's own voice when that fails. Hausa: recorded human clips, or the phone's Hausa voice if it has one | gTTS, recorded audio, the browser's speech engine | Optional |
| USSD/SMS service | Fixed verified answers on the phone screen (election dates, PVC questions, the 20 office addresses), typed questions and reports for a person to answer by SMS | Flask service on Africa's Talking (simulator only) | Separate prototype |

## 3. Intended use

- Answer common voter-information questions in Hausa, Fulfulde and English: where to collect a PVC, election dates, what to bring, where an INEC office is, which polling units are in a ward.
- Help citizens spot fake election messages.
- Be used by adults aged 18 and above in Bauchi State.

## 4. Out of scope (do not use for)

- Anything partisan: persuasion, microtargeting, opinions on parties, candidates or results.
- Legal advice, or deciding whether a person is allowed to vote or which polling unit is theirs. MURYA lists the units in a ward; a voter confirms their own unit on the PVC or with INEC.
- Access to the voter register, names or PVC numbers.
- Automatic publishing of answers without a person.
- Any use as an official INEC channel.
- Use during a live election, or against live electoral systems. The prototype is for testing with consenting adults and test or public information.
- Incident reporting as an official channel. The USSD "report a problem" path is a prototype.
- Collecting disability data or other sensitive details. The usability test asks only whether a person reads English and what kind of phone they use.

## 5. Data

| Data | Source | Size | Notes |
|---|---|---|---|
| Verified FAQs | Written in Hausa from INEC guidance, with English and Fulfulde versions | 4 | Each has a source and review date |
| INEC office addresses | INEC Bauchi State LGA directory, checked in person | 20 | Confirmed by the developer; INEC check requested |
| Polling units | **Synthetic** (real LGA names; made-up wards and units named SAMPLE; codes start with 00) | *(fill in: number loaded)* | Labelled "SAMPLE DATA" on the page; not for real use |
| Accessibility-barriers survey | **Synthetic** (the organisers' file, and a Bauchi version made for MURYA) | 500 + 500 | Shown on the Dashboard with a SYNTHETIC SAMPLE banner; not used to train or tune anything; no real pattern |
| USSD screens | The same verified facts as the web app, shortened to fit the phone screen | 75 screens | All plain ASCII and within 182 characters |
| Test questions | Written by the developer | 60 development + 37 noisy + 9 risk-flag tests | Not independent (see 6) |

Election dates come from INEC's revised 2027 timetable and must be re-checked at inec.gov.ng before launch.

## 6. Evaluation

Every method here only returns approved text or hands over to a person. **None can invent an answer.** What differs is how often each returns the right approved answer, a wrong one, or correctly hands over.

**Development set (60 questions).** Hausa, English and mixed wording, including off-topic questions that should return "no match". MURYA's matcher: **58/60** (the earlier keyword matcher: 44/60).

**Noisy held-out set (37 questions).** Typos, Hausa and English mixed in one sentence, voice-to-text style noise, very short low-literacy phrasing, and questions that should be handed to a person. Measured with `compare_retrieval.py`:

| Method | Development (60) | Noisy (37) |
|---|---|---|
| A. Plain TF-IDF word matching (starter-style baseline) | 49/60 | 30/37 |
| B. MURYA matcher, before the typo and spelling fix | 58/60 | 27/37 |
| B. MURYA matcher, after the typo and spelling fix | 58/60 | 34/37 |
| C. Multilingual embeddings | *(not yet run: `pip install sentence-transformers`, then re-run the script)* | *(not yet run)* |

What the noisy set found: the matcher was weaker than the baseline on spelling variants such as "colect", "chek", "ofice", "Torro", "fotokopi" and "ofis". The fix adds those spellings and reads a close typo as the nearest known word. Three misses remain, and an unrelated word such as "lokaci" (time) can still pull a question toward the election-date FAQ. A suggested FAQ is shown only as a "related answer" while a person replies.

**Limits of this evidence.** The developer wrote all the questions, and the noisy set's failures guided the fix, so the "after" score is optimistic. The fact base is tiny (4 FAQs and 20 offices), so this compares methods; it is not a measure of real-world accuracy. Re-run `compare_retrieval.py` on your own `app.py` and update this table.

**Risk flags.** 9/9 on a small hand-written test set.

**Unsupported answers.** None by design: every answer shown to a citizen is a fact a person approved, or it is a human-written reply.

**USSD screens.** All 75 screens are plain ASCII and within 182 characters. All 20 LGA offices can be reached through the paged menu and show the right address (tested).

**Accessibility audit.** Google PageSpeed Insights (Lighthouse), mobile, home page: Accessibility **96**, Best Practices 100, SEO 92, Performance 92. The one failing accessibility check was colour contrast; a fix darkens the small grey text. *(Fill in: the score after re-testing and the other pages tested.)* Manual checks with a screen reader (TalkBack), large text and high contrast are still to be reported.

**Pilot protocol.** The pilot uses the usability test sheet. Each volunteer is 18 or above and agrees first, and no name, phone number or PVC number is written down. There are two sets of three questions (A and B). One set is answered the volunteer's usual way and the other with MURYA, and the sets are swapped for the next volunteer, so nobody sees the same questions twice. The sheet records whether the answer was right, minutes taken, whether help was needed, ease of use, whether they would use it again, and any wrong or confusing answer. The target is at least 15 volunteers in three or more LGAs, including people who cannot read English.

**Pilot with real users.** *(Fill in after the test: people tested, correct without help before and after, median time, 👍 rate, wrong or confusing answers found.)*

## 7. Performance by language

| Language | Interface | Question matching | Voice in | Voice out | Native-speaker review |
|---|---|---|---|---|---|
| Hausa | Yes | Yes (60 + 37 question sets) | Whisper, accuracy not yet measured *(fill in word error rate)* | Recorded clips; the phone's Hausa voice if it has one; no server Hausa voice | *(Name and date of the reviewer)* |
| English | Yes | Yes | Whisper | Server voice, or the phone's voice | Developer |
| Fulfulde | Text only, hidden from citizens until a native speaker approves it | Via the Hausa and English facts | None; goes to a human | None | Required before citizens see it *(Name and date)* |

## 8. Known limitations and risks

- Very few facts, so most questions go to a human reviewer.
- The matcher can return a related but wrong FAQ for odd wording. A reviewer sees it before anything is published, but a citizen sees the suggested FAQ while waiting.
- Typo correction can read an unusual word as a nearby known word.
- Hausa speech recognition is weaker than English; Fulfulde has none. Many phones have no Hausa voice, so recorded clips are the reliable route for Hausa audio.
- The server voice is often blocked from cloud hosts. The phone's own voice is the fallback.
- The web app is heavy on 2G. USSD is the low-bandwidth route.
- Facts can go stale when INEC changes a date, an office or a polling unit. Every fact shows its source and review state.
- The polling-unit finder lists the units in a ward. It does not know which unit is a particular voter's.
- The accessibility-barriers section on the Dashboard reads made-up data. It shows how the page would work, not real findings about Bauchi voters.
- One reviewer is a bottleneck. An audit log records who confirmed or published what in the web app, but reviewers type their own names. The USSD dashboard has no audit log yet.
- The USSD service runs only in the simulator. Live use needs a registered short code and sender ID.
- Third-party services may process data outside Nigeria when switched on.

## 9. Human oversight and safeguards

- A person approves every published answer. AI drafts are grounded in confirmed facts only, are never sent automatically, and show "grounded: no" when the facts do not cover the question.
- Office answers show "awaiting human confirmation" until a person confirms them. The polling-unit list is synthetic, and the page says so in a banner, so nobody mistakes it for a real list.
- The Fulfulde text stays hidden from citizens until a native speaker approves it.
- USSD questions and reports are answered by a person from a password-protected dashboard.
- Risky messages are flagged for the reviewer, never silently blocked or auto-answered. Phone-style numbers, long ID numbers and email addresses are removed before a message is stored.
- Consent before storing, 30-day automatic deletion, anonymised exports. See `THREAT_MODEL.md` for security.

## 10. Fit with the Track 3 success criteria and red lines

| Criterion or red line | MURYA evidence | Status |
|---|---|---|
| Answer accuracy against approved sources | 58/60 on the development set and 34/37 on the noisy set; every answer is an approved fact | Developer-written sets; real-user pilot pending |
| Hallucination rate (target: zero unsupported answers) | None by design: approved text or a hand-over to a person | Met by design |
| Per-language quality with native-reviewer sign-off | Fulfulde hidden until a native speaker approves it; Hausa and English reviewers to be named | Reviewer names pending |
| WCAG audit results | Lighthouse accessibility 96 (mobile, home page); contrast fix applied; screen-reader test to report | Partly done |
| Usability test with real users, with consent | Test sheet ready (consent, swapped question sets, no names) | Not yet run |
| Works on low-end phones and 2G | USSD/SMS path; the web app is heavy on 2G and still to be tested on a throttled "Slow 3G" connection | USSD yes; web partly |
| Red line: no invented electoral rules or dates | Facts come from INEC sources, with dates, and tell voters to confirm at inec.gov.ng | Ask INEC to confirm the four FAQs |
| Red line: no advice that could disenfranchise | Only confirmed facts are shown as verified; the PVC rule needs INEC's written confirmation | In progress |
| Red line: no disability data without consent and need | Not collected | Met |

## 11. Maintenance

Re-verify each fact against INEC on a fixed schedule and before any election milestone. Review the risk-flag rules weekly during the election period. Re-run the self-test and `compare_retrieval.py` after any change to the facts or the matcher, and add real questions from the pilot to the test sets.

## 12. Licence and credits

Licence: *(to be added)*. Third-party libraries keep their own licences. The INEC logo is not covered by MURYA's licence and is used with INEC's permission. The synthetic polling-unit data and its generator are covered by it.

## 13. Contact

Zaharaddeen Muhammad, Bauchi, Nigeria. Use the Ask page of the app.

*MURYA is an independent project. It is not an INEC product.*
*Last updated: 3 November 2026.*
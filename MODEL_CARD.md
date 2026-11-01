# MURYA model card

AI4Elections Hackathon 2026–2027 · Track 3 · Version 1 (prototype)

## 1. System summary

MURYA (Muryar Zabe) is a voter-information helpdesk for Bauchi State. It is a **retrieval system with human approval**, not a text generator. It matches a citizen's question to a fact that a person has already verified, and shows the source. When it cannot match, a person answers.

**MURYA does not train or fine-tune any model.** It uses no personal data for training.

## 2. Components

| Component | What it does | Provider / method | Required? |
|---|---|---|---|
| Answer matching | Finds the closest verified fact | Our own code: Hausa and English concept matching with word stems and rarity weighting | Yes |
| Risk flags | Marks links, vote-buying, rumours (including flood-linked), phone numbers, party names | Regular-expression rules | Yes |
| Speech-to-text | Turns Hausa or English voice notes into text for the reviewer | OpenAI Whisper (`whisper-1`) | Optional |
| Draft assistant | Suggests a reply from confirmed facts only; a person edits and publishes | Anthropic model (default `claude-haiku-5-5`) | Optional |
| Text-to-speech | Reads English answers aloud; Hausa uses recorded human clips | gTTS (Google) and recorded audio | Optional |
| USSD/SMS | Citizens without smartphones; a person replies | Africa's Talking (simulator) | Separate prototype |

## 3. Intended use

- Answer common voter-information questions in Hausa, Fulfulde and English: where to collect a PVC, election dates, what to bring, where an INEC office is, which polling units are in a ward.
- Help citizens spot fake election messages.
- Be used by adults aged 18 and above in Bauchi State.

## 4. Out of scope (do not use for)

- Anything partisan: persuasion, microtargeting, opinions on parties, candidates or results.
- Legal advice, or deciding whether a person is allowed to vote.
- Access to the voter register, names or PVC numbers.
- Automatic publishing of answers without a person.
- Any use as an official INEC channel.

## 5. Data

| Data | Source | Size | Notes |
|---|---|---|---|
| Verified FAQs | Written in Hausa from INEC guidance, with English and Fulfulde versions | 4 | Each has a source and review date |
| INEC office addresses | INEC Bauchi State LGA directory, checked in person | 20 | Confirmed by the developer; INEC check requested |
| Polling units | INEC Bauchi State Office (authorised use) | *(fill in)* | Shows list date and confirmation state |
| Test questions | Written by the developer | 60 + 9 flag tests | Not independent (see 6) |

Election dates come from INEC's revised 2027 timetable and must be re-checked at inec.gov.ng before launch.

## 6. Evaluation

**Answer matching.** 60 hand-written questions in Hausa, English and mixed wording, including off-topic questions that should return "no match". Result: **58/60** correct, against 44/60 for the earlier keyword matcher. On 22 questions written later, it scored 20/22 (14/22 before). The misses return a related FAQ for the reviewer to see.

**Limits of this evidence.** The developer wrote the questions and tuned the matcher on part of them. The fact base is tiny, so this is a sanity check, not a measure of real-world accuracy.

**Risk flags.** 9/9 on a small hand-written test set.

**Unsupported answers.** None by design: every answer shown to a citizen is a fact a person approved, or it is a human-written reply.

**Pilot with real users.** *(Fill in after the test: people tested, correct without help before and after, median time, 👍 rate.)*

## 7. Performance by language

| Language | Interface | Question matching | Voice in | Voice out | Native-speaker review |
|---|---|---|---|---|---|
| Hausa | Yes | Yes (60-question set) | Whisper, accuracy not yet measured *(fill in word error rate)* | Recorded clips; no synthetic Hausa voice | *(Name and date of the reviewer)* |
| English | Yes | Yes | Whisper | Synthetic voice | Developer |
| Fulfulde | Text only, after approval | Via the Hausa/English facts | None; goes to a human | None | Required before citizens see it *(Name and date)* |

## 8. Known limitations and risks

- Very few facts, so most questions go to a human reviewer.
- The matcher can return a related but wrong FAQ for odd wording, such as "Ba tare da kati ba, ana zabe?". A reviewer sees it before anything is published, but a citizen sees the suggested FAQ while waiting.
- Hausa speech recognition is weaker than English; Fulfulde has none.
- Facts can go stale when INEC changes a date or an office. Every fact shows its source and review state.
- One reviewer is a bottleneck. An audit log records who confirmed or published what, but reviewers type their own names.
- Third-party services may process data outside Nigeria when switched on.

## 9. Human oversight and safeguards

- A person approves every published answer. AI drafts are grounded in confirmed facts only, are never sent automatically, and show "grounded: no" when the facts do not cover the question.
- Office answers show "awaiting human confirmation" until a person confirms them.
- The Fulfulde text stays hidden from citizens until a native speaker approves it.
- Risky messages are flagged for the reviewer, never silently blocked or auto-answered. Phone-style numbers, long ID numbers and email addresses are removed before a message is stored.
- Consent before storing, 30-day automatic deletion, anonymised exports. See `THREAT_MODEL.md` for security.

## 10. Maintenance

Re-verify each fact against INEC on a fixed schedule and before any election milestone. Review the risk-flag rules weekly during the election period. Re-run the self-test after any change to the facts or the matcher.

## 11. Contact

Zaharaddeen Muhammad, Bauchi, Nigeria. Use the Ask page of the app.

*MURYA is an independent project. It is not an INEC product.*

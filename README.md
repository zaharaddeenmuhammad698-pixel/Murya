# MURYA (Muryar Zabe): Voice of the Election

**Verified election information for Bauchi voters in Hausa, Fulfulde and English, by voice, text and USSD/SMS.**

AI4Elections Hackathon 2026–2027 · Track 3: Inclusive and Multilingual Electoral/Civic Technology
Built by Zaharaddeen Muhammad · Bauchi, Nigeria

> MURYA is an independent, non-partisan civic-tech project. It is **not** an INEC product and is not endorsed by INEC. Always confirm critical information at inec.gov.ng or at your local INEC office.

---

## 1. The problem and who it is for

Election information in Nigeria is mostly published in English, on websites and printed notices. In Bauchi State many voters speak Hausa or Fulfulde, some cannot read, and many use basic phones with limited data. They often learn where to collect a PVC or when to vote from WhatsApp messages and word of mouth, so rumours and scams spread faster than official information. Floods and weak networks make this worse.

**Intended users:** voters aged 18 and above in Bauchi's 20 LGAs, especially people who cannot read English, speak only Hausa or Fulfulde, use feature phones, or live where data networks are weak.

**What MURYA does:** a citizen asks a question by voice, text or USSD/SMS. MURYA matches it to an answer that a person has already verified against INEC sources and shows the source. If it cannot match, a human reviewer answers. AI never publishes an answer on its own.

## 2. Features

| Area | What it does |
|---|---|
| Ask | Text or voice question in Hausa, Fulfulde or English. A person replies by text or voice; replies are delivered as soon as they are sent. Citizens can rate each answer 👍/👎. |
| Verified Info | Human-approved FAQs with their source, plus a tap-to-pick list of the 20 LGAs showing the INEC office address. Read aloud. |
| Polling Units | Choose LGA, then ward, to see the polling units, or search by code or name. Loaded from the INEC list; shows the list date and whether INEC has confirmed it. Searches are not saved. |
| Learn | A short lesson on spotting fake election messages, with made-up examples. |
| Languages | Hausa and English interface. Fulfulde text appears for citizens only after a native speaker approves it. |
| Accessibility | Large text, high contrast, icon-first buttons, voice output, phone-friendly layout. |
| Dashboard | Aggregate figures only: questions per day, text vs voice, topics, share found helpful. |
| Admin | Review queue, publish or unpublish, fact base editor, voice-reply recorder, self-test, polling-unit import, Fulfulde review, data export and purge. |
| USSD/SMS | A separate prototype built on Africa's Talking (simulator): the citizen dials a USSD code and describes the problem; the admin reviews and replies by SMS from the sender name **MURYA**. *(Fill in: repository folder, code name and flow.)* |

## 3. How it works (methodology)

```
Citizen (voice / text / USSD)
        │
        ▼
 Speech-to-text (Hausa, English; Fulfulde goes straight to a human)
        │
        ▼
 Risk flags ── link, vote-buying, rumour, flood-rumour, contact request, partisan
        │
        ▼
 Retrieval: match to a human-verified fact ──► shown with its source
        │                                         (office answers marked "awaiting
        │ no match / unconfirmed                   human confirmation" until a
        ▼                                          person confirms them)
 Human reviewer: edits and publishes (optionally an AI draft, grounded in confirmed facts only)
        │
        ▼
 Reply delivered as text, audio and (USSD flow) SMS
```

**Answer matching (pure retrieval, nothing is generated).** Each verified fact is described by its Hausa question, its English question and keywords. Questions and facts are reduced to *concepts* so Hausa and English wording meet (for example "katina", "card" and "PVC" are one concept; "yaushe" and "when" are one concept), plus a 4-letter stem so word endings match. Concepts are weighted by how rare they are across the fact base. A match needs a score of at least 0.34 and either two shared concepts, or one distinctive concept. Questions that share only a common word, such as "Who should I vote for?", return no match and go to a human.

**Office-location questions.** A question naming an LGA together with an office word returns that LGA's INEC office address. The address is shown with an "awaiting human confirmation" note until a person confirms it in Admin.

**Risk flags.** Regular-expression rules mark messages containing links, vote-buying offers, rumours (for example "postponed", "cancelled"), flood-linked rumours ("ambaliya" or "flood" together with an election word), phone numbers and party names. Flags help the reviewer; they do not block anything.

**Optional AI draft.** If an Anthropic API key is set, the reviewer can request a draft reply. The model is given only the confirmed facts and must say "not grounded" when they do not answer the question. A person edits and publishes; the draft is never sent automatically.

**Speech and audio.** Hausa and English voice notes are transcribed with Whisper when an OpenAI key is set. There is no speech recognition for Fulfulde. Text-to-speech (gTTS) has no Hausa voice, so Hausa answers play human-recorded clips from `voice_audio/` when they exist; the Admin "Voice clips" tab records and stores them.

**Languages and review.** Every fact can carry an English and a Fulfulde version. English text is shown when present. Fulfulde text is hidden from citizens until a native speaker approves it in Admin; until then citizens see Hausa with a "translation pending" note.

## 4. Data and sources

| Data | Source | Status |
|---|---|---|
| 20 LGA INEC office addresses | INEC Bauchi State LGA office directory (inecnigeria.org), checked in person by the developer | Confirmed in Admin |
| Election dates (16 Jan 2027 presidential and National Assembly; 6 Feb 2027 governorship and State Assembly) | INEC's revised 2027 timetable as reported in Feb 2026; confirm at inec.gov.ng | Re-check before launch |
| Polling-unit list | INEC Bauchi State Office, used with written authorisation | *(Fill in date, and whether INEC has confirmed it)* |
| FAQs | Written in Hausa from INEC guidance | Source shown with each answer |

No voter register, names or PVC numbers are used. Only public, synthetic or expressly authorised data is used.

## 5. Evaluation

**Matching self-test (in the app, Responsible AI page).** 60 hand-written questions (Hausa, English, mixed, and off-topic ones that should return no match) against the 4 seed FAQs. Result on the live-like fact base: **58 of 60** correct, up from 44 of 60 with the earlier keyword matcher. A further 22 questions written after the first version scored 20 of 22 (14 of 22 before). The two misses return a related FAQ, which a reviewer would see.

*Caveat:* the questions were written by the developer, and part of the set was used to tune the matcher. Treat this as a sanity check, not a benchmark. Risk flags: 9 of 9 on their small test set.

**Pilot with real users.** *(Fill in after the test.)*

| Measure | Usual way | With MURYA |
|---|---|---|
| People tested (of whom cannot read English) | | |
| Got the right answer without help | % | % |
| Median time to answer | min | min |
| Rated the answer helpful | | % |
| Median time from question to approved reply | | min |
| Hausa speech-to-text word error rate (20 recordings) | | % |

**Accessibility audit.** *(Fill in: Lighthouse accessibility score and what was fixed.)*

## 6. Responsible AI, privacy and security

- **Human in the loop.** No answer is published without a person. AI only transcribes, matches or drafts.
- **Non-partisan.** MURYA never gives opinions on parties, candidates or results; partisan content is flagged.
- **Consent.** Citizens agree before anything is stored. A data-protection note (Hausa and English) follows the principles of the Nigeria Data Protection Act 2023. It has not yet had a legal review.
- **Data minimisation.** No names, PVC numbers or phone numbers are requested. Polling-unit searches are not saved.
- **Retention and deletion.** Messages and voice notes are deleted automatically after 30 days (configurable). Citizens can delete their own messages during their visit.
- **Access.** Citizens see only their own messages. Public pages show totals and approved answers only. Admin uses a salted PBKDF2-SHA256 hash (200,000 iterations) with lockout after 5 wrong attempts. Messages are rate-limited to 15 per hour per session. Exports are anonymised.
- **Third parties (only when switched on).** Voice goes to a speech-to-text provider, question text to an AI drafting service, and answer text to Google for reading aloud. These may process data outside Nigeria.
- **Climate resilience.** USSD/SMS works without mobile data, which matters when floods disrupt networks. Flood-linked rumours about postponed elections are flagged.

## 7. Limitations (honest account)

- The verified fact base is small: 4 FAQs and 20 office answers. Matching is only as good as the facts behind it.
- Hausa speech recognition is weaker than English. Fulfulde has none, so those voice notes need a human.
- Text-to-speech has no Hausa voice. Recorded clips are needed for good Hausa audio.
- The Fulfulde wording needs a native speaker's approval before it goes live.
- The USSD/SMS prototype runs in the Africa's Talking simulator only. A live short code and sender ID need operator approval.
- One admin password and no audit log of who changed what. One reviewer is a bottleneck.
- Free hosting can erase the database on restart; a managed database is needed for production.
- Streamlit is heavy on 2G. USSD is the low-bandwidth path.
- A person's own polling unit is confirmed on their PVC or with INEC. The finder lists units in a ward.
- The pilot is small and not statistically representative.

## 8. Pathway to further development

1. Agree with INEC Bauchi who verifies content, and refresh it from official sources.
2. Train volunteer reviewers in shifts, and add reviewer accounts with an audit log.
3. Move to a managed database; add a tamper-evident log.
4. Take USSD/SMS live with a registered short code and sender ID; add an IVR line.
5. Native-speaker review for Hausa and Fulfulde, recorded audio for every answer, and more Nigerian languages.
6. USSD polling-unit lookup (LGA, ward, units).

## 9. Run it yourself

**Requirements:** Python 3.10 or later and the packages `streamlit`, `requests`, `gTTS`, `pandas` (add `openpyxl` to import Excel files).

```bash
pip install streamlit requests gTTS pandas openpyxl
streamlit run app.py
```

**Optional secrets** (Streamlit secrets or environment variables):

| Name | Purpose |
|---|---|
| `OPENAI_API_KEY` | Turns on speech-to-text for Hausa and English voice notes |
| `ANTHROPIC_API_KEY` | Turns on the AI draft button for reviewers |
| `ANTHROPIC_MODEL`, `STT_MODEL` | Override the default models |
| `RETENTION_DAYS` | Days before messages are deleted (default 30) |

Without any keys the app still works in human-only mode.

**Files:** `app.py` (the whole app), `murya.db` (created on first run), `voice_audio/` (recorded answer clips), `voice_notes/` (incoming and reply audio), `assets/inec_logo.png` (optional INEC logo, shown only as a source badge).

**Admin:** open the Admin page and sign in. Queue: review and publish. Fact base: edit and confirm facts, and add English and Fulfulde versions. Voice clips: record Hausa and Fulfulde audio. Polling units: import the INEC list. Languages: approve Fulfulde. Data and privacy: export, purge.

## 10. Credits

Built for the AI4Elections Hackathon 2026–2027 (Rise Networks, in collaboration with INEC and partners). INEC office information from the INEC Bauchi State directory. Thanks to the volunteers who tested the prototype.

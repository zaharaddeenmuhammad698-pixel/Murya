# MURYA datasheet

Data used or created by MURYA, in the style of "datasheets for datasets". Version 1.0 · 3 November 2026.

## 1. Why the data exists

To answer common voter-information questions for Bauchi State in Hausa, Fulfulde and English, from facts a person has verified, and to test whether the matcher finds the right fact.

## 2. The datasets

| Dataset | What it contains | Size | Source | Status |
|---|---|---|---|---|
| Verified FAQs | Question, answer, keywords, source and review date, in Hausa with English and Fulfulde versions | 4 | Hausa text written by the developer from INEC guidance; English drafted with AI assistance and checked by the developer; Fulfulde drafted with AI assistance, **not yet reviewed by a native speaker** | Hausa and English in use; Fulfulde hidden from citizens until approved |
| INEC office addresses | One address per Bauchi LGA | 20 | INEC Bauchi State LGA directory (2024), checked in person by the developer | Confirmed by the developer; INEC check requested |
| Polling units | LGA, ward, polling-unit code, name | *(fill in)* | INEC Bauchi State Office, used with written permission | Imported in Admin; shows list date and confirmation |
| Matching test sets | Development set (60 questions), noisy set (37 questions), risk-flag tests (9) | 106 | Written by the developer | Not independent; the noisy set's failures guided a fix |
| USSD screens | The verified facts shortened for a phone screen | 75 | Derived from the verified facts | Plain ASCII, within 182 characters |
| Usability test sheets | Task results by volunteer code | *(fill in)* | The pilot | No names, phone numbers or PVC numbers |
| Citizens' messages and USSD reports | Questions, voice notes, replies, report text | live data | Citizens, with consent | Numbers removed before saving; deleted after 30 days |

## 3. How the data was collected and cleaned

- Office addresses came from INEC's published directory. Two road names that were garbled in the source were left out and only landmarks kept.
- Election dates follow INEC's revised 2027 timetable and are re-checked before launch.
- Citizens' messages have phone-style numbers, long ID numbers and email addresses removed before they are stored. Risk flags are worked out first, on the original text.

## 4. People and consent

- Every volunteer is 18 or above and agrees before taking part. The consent text is read in the volunteer's language.
- No names, phone numbers, PVC numbers or disability data are collected. The test sheet asks only whether a person reads English and what kind of phone they use.
- USSD users' phone numbers are kept only so a reviewer can reply. The dashboard masks them, exports leave them out, and they are deleted after 30 days.

## 5. Intended and unintended uses

- **Intended:** answering voter-information questions, testing retrieval methods, teaching how to spot fake election messages.
- **Not intended:** profiling people, targeting or persuading voters, learning anything about the voter register, or any use in a live election without INEC's agreement.

## 6. Distribution and licence

- The verified facts, the office list, the test sets and the code can be shared once a licence is added.
- The INEC logo and INEC's polling-unit list are **not** covered by MURYA's licence and are used with INEC's permission. Do not publish the polling-unit list unless INEC allows it.
- `murya.db`, `voice_notes/` and anything with citizens' messages must never be committed to a public repository.

## 7. Maintenance

Re-check every fact against INEC on a fixed schedule and before any election milestone. Re-check the polling-unit list when INEC publishes a new one. Add real questions from the pilot to the test sets.

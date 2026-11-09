# MURYA datasheet

Data used or created by MURYA, in the style of "datasheets for datasets". Version 1.0 · 3 November 2026.

## 1. Why the data exists

To answer common voter-information questions for Bauchi State in Hausa, Fulfulde and English, from facts a person has verified, and to test whether the matcher finds the right fact.

## 2. The datasets

| Dataset | What it contains | Size | Source | Status |
|---|---|---|---|---|
| Verified FAQs | Question, answer, keywords, source and review date, in Hausa with English and Fulfulde versions | 4 | Hausa text written by the developer from INEC guidance; English drafted with AI assistance and checked by the developer; Fulfulde drafted with AI assistance, **not yet reviewed by a native speaker** | Hausa and English in use; Fulfulde hidden from citizens until approved |
| INEC office addresses | One address per Bauchi LGA | 20 | INEC Bauchi State LGA directory (2024), checked in person by the developer | Confirmed by the developer; INEC check requested |
| Polling units | LGA, ward, polling-unit code, name | *(fill in)* | **Synthetic**: made with `make_synthetic_polling_units.py` (or the organisers' synthetic file). The 20 LGA names are real; every ward and unit is made up and named SAMPLE; codes start with 00, which no real INEC state uses | Labelled "SAMPLE DATA" in the app; not for real use |
| Accessibility-barriers survey | Respondent code, area (state or LGA), settlement, age band, gender, disability type, preferred language, main barrier, simulated voting, confidence finding information (1 to 5) | 500 (organisers' file, 20 states) and 500 (Bauchi version, 25 per LGA) | **Synthetic.** The organisers' file, and `make_synthetic_barriers_bauchi.py` (real LGA names, languages Hausa/Fulfulde/English, every answer drawn at random with a fixed seed) | Shown on the Dashboard with a SYNTHETIC SAMPLE banner. No real pattern in either file. MURYA collects no disability data |
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
- The survey files have a disability-type column because the organisers' layout does. The answers are made up. MURYA's own forms never ask about disability.
- USSD users' phone numbers are kept only so a reviewer can reply. The dashboard masks them, exports leave them out, and they are deleted after 30 days.

## 5. Intended and unintended uses

- **Intended:** answering voter-information questions, testing retrieval methods, teaching how to spot fake election messages.
- **Not intended:** profiling people, targeting or persuading voters, learning anything about the voter register, or any use in a live election without INEC's agreement.

## 6. Distribution and licence

- The verified facts, the office list, the test sets and the code can be shared once a licence is added.
- The INEC logo is **not** covered by MURYA's licence and is used with INEC's permission. The synthetic polling-unit data and its generator can be shared. The synthetic survey files and their generator can be shared too.
- `murya.db`, `voice_notes/` and anything with citizens' messages must never be committed to a public repository.

## 7. Maintenance

Re-check every fact against INEC on a fixed schedule and before any election milestone. If a real list is ever loaded, it needs INEC's written permission and its date shown. Add real questions from the pilot to the test sets.

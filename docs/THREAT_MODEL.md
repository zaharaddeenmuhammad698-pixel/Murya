# MURYA threat model

AI4Elections Hackathon 2026–2027 · Track 3 · Version 1.2 · Method: STRIDE (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), applied to what is actually built.

## 1. What we protect, and from whom

**Assets**
1. The integrity of the verified answers (a wrong office address, date or polling unit could turn a voter away).
2. Citizens' messages and voice notes, and the phone numbers of people who use USSD/SMS (they may contain personal details even though we ask people not to share them).
3. The admin consoles (web app and USSD dashboard) and their credentials.
4. Trust in MURYA's name (it must not be mistaken for INEC, and no one should be able to pose as MURYA).

**Who might attack or misuse it:** rumour spreaders, scammers and vote-buyers, a party-political actor trying to use it for persuasion, a curious or malicious visitor, a careless insider.

**Components**
- Streamlit web app (`app.py`) with a SQLite database, audio files and an imported polling-unit list.
- Flask USSD/SMS service (`ussd.py`) with its own SQLite database and a reviewer dashboard, built on Africa's Talking (simulator only).
- Optional outside services: speech-to-text, AI drafts, server text-to-speech, and the phone's own speech engine.
- The hosting platform and the GitHub repository.

## 2. Threats, controls and gaps

| # | Threat (STRIDE) | Example | Controls in place | Gap | Fix (priority) |
|---|---|---|---|---|---|
| 1 | **Spoofing** the brand | A lookalike site or SMS pretending to be MURYA or INEC | "Independent, not INEC" notice on every page; the INEC logo only as a labelled source badge | No official domain or registered sender ID yet | Use one fixed domain; register the "MURYA" sender ID before any live launch (High) |
| 2 | **Spoofing** the web admin | Guessing the admin password | Salted PBKDF2-SHA256 hash (200,000 iterations) read from secrets (`ADMIN_PW_SALT`, `ADMIN_PW_HASH`, made with the one-line command in the README, since the helper scripts are not in the repository); lockout after 5 wrong tries in 5 minutes, counted in the database across all sessions; reviewer name required | The old fallback hash is still in `app.py` until it is deleted; an attacker can lock the admin out for 5 minutes | Delete `PW_SALT` and `PW_HASH` from the code once secrets work; use a 14+ character passphrase (High) |
| 3 | **Spoofing** the USSD dashboard | Guessing the dashboard password; stealing the sign-in | A real sign-in page with a cookie session (12 hours); password stored only as a hash in the host's Environment page (`ADMIN_PASSWORD_HASH`); 8 wrong tries lock the address for 5 minutes; secure, HTTP-only cookies; forms protected against forged requests; pages marked do-not-index and no-store; plain-English hints when the stored hash is damaged | One shared account; the lockout counter lives in each worker's memory, so a restart clears it; anyone with access to the host's Environment page can read the hash | Individual accounts; move the counter to the database; limit who can open the host dashboard (Medium) |
| 4 | **Spoofing** the USSD callback | Someone posts fake reports to the service | The callback address contains a long secret token (`USSD_TOKEN`); a wrong or missing token returns "not found" | The token appears in the callback address and may appear in host logs | Rotate the token if it leaks; keep logs private (Medium) |
| 5 | **Tampering** with answers | A compromised admin edits a fact, imports a bad polling-unit list, or edits the database file | Facts carry a source and a reviewed date; office answers show "awaiting human confirmation" until confirmed; polling-unit import needs a permission tick, shows the list date and "awaiting INEC confirmation" until INEC confirms; every change is attributed to a named reviewer in the audit log | One shared password; no integrity check on the database files | Individual reviewer accounts; backups; a "last reviewed" re-check date (Medium) |
| 6 | **Repudiation** | "I never published that wrong answer" | **Audit log in the web Admin:** reviewer name, action and time for logins, failed logins, publishing, unpublishing, deletions, fact and translation edits, polling-unit imports, exports and purges. Message text is never logged | The log is in the same database, so someone with database access could edit it. The USSD dashboard has no audit log yet | Add an audit table to the USSD service; tamper-evident (hash-chained) logs and individual accounts later (Medium) |
| 7 | **Information disclosure** of web messages | Someone reads another citizen's messages; a leaked database | Citizens see only their own session's messages; exports drop the session ID; 30-day automatic deletion; consent and a data-protection note; phone numbers, long ID numbers and email addresses are removed before a message is stored (flagged "number-removed") | Stored unencrypted; a voice recording can still contain spoken details; names and addresses are not detected | Encrypt the database or use a managed one; tell citizens that voice notes can hold personal details (done in the privacy note) (Medium) |
| 8 | **Information disclosure** on the USSD side | A leaked database or export reveals phone numbers | The number is kept only so a reviewer can reply; the dashboard shows it masked (for example +234****567); the CSV export has no numbers, only a short one-way code; descriptions are cleaned of numbers and emails; reports are deleted after 30 days; the reviewer can delete any report | Numbers are stored unencrypted in the database; the privacy note must say numbers are kept for replies | Encrypt or hash numbers once replies are done; add the line to the privacy note (High) |
| 9 | **Information disclosure** to third parties | Text, voice or answers sent to outside services | Speech-to-text and AI drafts are off unless a key is set; disclosed in the privacy note; Fulfulde is not sent to speech recognition. Listening works in two ways: the server voice (Google's gTTS) for English, or, when that fails or for Hausa, a "Tap to hear" button that makes the phone read the text itself | Providers may process data outside Nigeria. Depending on the phone, its own speech engine may also use an online voice | Keep outside services off for the pilot unless needed; review provider terms (Medium) |
| 10 | **Denial of service** | Flooding the app with messages or large audio; guessing logins | Web: 15 messages per hour per session, 10 MB audio limit. USSD: 5 messages per number per hour | A new web session resets its limit; free hosting has its own limits | Rate-limit at the host or proxy and per device; cap daily totals (Medium) |
| 11 | **Elevation of privilege** via the AI | A citizen message that tells the AI draft to ignore its rules ("prompt injection") | The message is treated as untrusted data; the AI sees only confirmed facts; a person edits and publishes every draft | A busy reviewer could trust a bad draft | Show "grounded: no" prominently; never auto-publish (kept) (Low) |
| 12 | **Misuse for persuasion or abuse** | Vote-buying offers, partisan messages, scams | Risk flags (link, vote-buying, rumour, flood-rumour, contact request, partisan) for the reviewer; no persuasion features | Flags are rules, so they miss new wording | Review the flag list weekly during the election period (Medium) |
| 13 | **Wrong or stale information** | A date, address or polling unit changes after publication | Source and date per fact; election dates re-checked against INEC; the polling-unit page shows the list date, says whether INEC has confirmed it, and asks voters to confirm their own unit on the PVC or with INEC; searches are not saved | Nobody is reminded to re-check | Add a re-verification schedule; link to INEC's official timetable (High) |
| 14 | **Wrong match** | A typo or odd wording makes the matcher return a related but wrong FAQ | A suggested FAQ is only a "related answer" while a person replies; the matcher hands over to a human when nothing fits; typos are read as the nearest known word only when very close; test sets include typos, mixed Hausa/English and voice-to-text noise | The matcher can still match an unusual word to a nearby known one | Keep adding real questions from the pilot to the test set (Medium) |
| 15 | **Repo and supply-chain leaks** | Secrets, the database or old backups committed to GitHub; a vulnerable library | Secrets live in the host's Environment page; the helper scripts are kept out of the repository by `.gitignore` (and contain no secrets); the same `.gitignore` should also exclude the database, voice notes, `.bak` files and secrets | No licence file yet; libraries are not pinned; the INEC logo and polling-unit list need separate permission | Add `.gitignore` and a `LICENSE`; pin library versions; exclude the INEC logo and list from the open licence (Medium) |
| 16 | **Platform loss** | Free hosting wipes the databases on restart | Admin can export data | No backups | Managed database and scheduled backups (Medium) |
| 17 | **Advice that could disenfranchise** | A wrong rule or date makes someone stay at home, for example "you must have your original PVC", or an election date that has changed | Only confirmed facts are shown as verified; answers say "confirm at inec.gov.ng"; dates and the PVC rule come from INEC sources and are re-checked; the polling-unit page asks voters to confirm their own unit on the PVC or with INEC; the Track 3 red lines (no invented rules or dates) guide every FAQ | INEC has not yet confirmed the four FAQs, the election dates or the PVC rule in writing | Ask INEC Bauchi to confirm them; record who confirmed and when (High) |
| 18 | **Visitor tracking by outside sites** | The page loads a web font from Google, so Google can see each visitor's address | MURYA itself sends nothing personal to the font service | The font loads from fonts.googleapis.com on every page view | Use a system font or host the font file yourself (Low) |
| 19 | **Leftover test and debug aids** | `?debug=1` shows the session code on screen; `.bak` files hold the previous admin hash; helper scripts sit in the project folder | The debug line shows only a random session code, which gives no access to anyone's messages; the helper scripts are listed in `.gitignore`, so they are not uploaded, and contain no secrets | A `.bak` file or `murya.db` could be committed to a public repository by mistake | Add `.gitignore`; delete `.bak` files once the app works; remove the debug line before launch if you prefer (Low) |

## 3. Residual risk we accept for the prototype

- One reviewer and a small fact base. Human error is possible, so every office address, date and polling-unit list shows its source and review state.
- The pilot uses only consenting adults and no real PVC numbers. The USSD service runs in the simulator with test data only, never against a live election.

## 4. Priority fixes before any live use

1. ~~Admin hash out of the code and a database-based lockout~~ done for the web app (delete the old fallback values and set a strong passphrase). USSD dashboard: password hash in the Environment page, done.
2. Audit log: **done** for the web app; still to do for the USSD dashboard. Individual reviewer accounts still to do.
3. ~~Removal of phone-like numbers before storing~~ done for both services (voice recordings and free-text names are not covered).
4. Managed database with backups for both services.
5. A registered sender ID, and encrypting or hashing phone numbers once a reply is sent.
6. A re-verification schedule for every fact and for the polling-unit list.
7. Repo hygiene: `.gitignore` (the helper scripts are done; add the database, voice notes, `.bak` files and secrets if not yet), a `LICENSE`, pinned libraries, and nothing secret in the repository.
8. Written confirmation from INEC of the four FAQs, the election dates and the PVC rule (risk 17).

## 5. What changed since version 1

**Since version 1.1 (3 November 2026)**
- New rows 17 to 19: advice that could disenfranchise, visitor tracking by the font service, and leftover test and debug aids.
- The sign-in page for the USSD dashboard was tested against the usual causes of a loop (quote marks or spaces around the hash, a capital letter in the user name, a space after the password, a blocked cookie), and a local checker (kept outside the repository) confirms that the hash and the password match before anything is deployed.
- The helper scripts were moved out of the repository and listed in `.gitignore`. The README now has one-line commands to create the secrets, so setup does not depend on them.
- A usability test sheet was added. It uses consent, two swapped question sets and no names, phone numbers or PVC numbers, so the pilot data stays free of personal details.
- The typo fix was measured on a held-out noisy set (27/37 before, 34/37 after); the remaining wrong-match risk is row 14.

**Since version 1**

- A proper sign-in page for the USSD dashboard, with forged-request protection, hint messages and a lockout.
- A secret token in the USSD callback address; phone numbers masked in the dashboard and removed from exports.
- Typo-tolerant matching; the phone's own voice as a fallback for the Listen button.
- Polling-unit finder, with a permission tick, list date and confirmation state.
- Risks 3, 4, 8, 14 and 15 are new rows.

*Last updated: 3 November 2026. Owner: Zaharaddeen Muhammad.*

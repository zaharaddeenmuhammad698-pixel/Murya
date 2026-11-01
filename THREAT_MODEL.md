# MURYA threat model

AI4Elections Hackathon 2026–2027 · Track 3 · Method: STRIDE (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), applied to what is actually built.

## 1. What we protect, and from whom

**Assets**
1. The integrity of the verified answers (a wrong office address or date could turn a voter away).
2. Citizens' messages and voice notes (they may contain personal details even though we ask people not to share them).
3. The admin console and its credentials.
4. Trust in MURYA's name (it must not be mistaken for INEC, and no one should be able to pose as MURYA).

**Who might attack or misuse it:** rumour spreaders, scammers and vote-buyers, a party-political actor trying to use it for persuasion, a curious or malicious visitor, a careless insider.

**Components:** Streamlit web app, SQLite database, audio files on the server, optional third-party services (speech-to-text, AI drafts, text-to-speech), and a separate USSD/SMS prototype (Africa's Talking).

## 2. Threats, controls and gaps

| # | Threat (STRIDE) | Example | Controls in place | Gap | Fix (priority) |
|---|---|---|---|---|---|
| 1 | **Spoofing** the brand | A lookalike site or SMS pretending to be MURYA or INEC | Prominent "independent, not INEC" notice on every page; INEC logo only as a source badge | No official domain or registered sender ID yet | Use one fixed domain; register the "MURYA" sender ID before any live launch (High) |
| 2 | **Spoofing** the admin | Guessing the admin password | Salted PBKDF2-SHA256 hash (200,000 iterations) read from secrets (`ADMIN_PW_SALT`, `ADMIN_PW_HASH`, made with `make_admin_hash.py`); lockout after 5 wrong tries in 5 minutes, counted in the database across all sessions; reviewer name required | **Fixed in code.** Remaining: the old fallback hash is still in `app.py` until you delete it; an attacker can lock the admin out for 5 minutes | Delete `PW_SALT` and `PW_HASH` from the code once secrets work; use a 14+ character passphrase (High) |
| 3 | **Tampering** with answers | A compromised admin edits a fact or the database file | Facts carry a source and a reviewed date; office answers show "awaiting human confirmation" until confirmed; every change is attributed to a named reviewer in the audit log | One shared password; no integrity check on the database file | Individual reviewer accounts; database backups; "last reviewed" re-check date (Medium) |
| 4 | **Repudiation** | "I never published that wrong answer" | **Audit log in Admin:** who (reviewer name), what and when for logins, failed logins, publishing, unpublishing, deletions, fact and translation edits, polling-unit imports, exports and purges. Message text is never logged | The log lives in the same database, so someone with database access could edit it; reviewers type their own name | Tamper-evident (hash-chained) log and individual accounts later (Medium) |
| 5 | **Information disclosure** of messages | Someone reads another citizen's messages; a leaked database | Citizens see only their own session's messages; exports drop the session ID; 30-day automatic deletion; consent and a data-protection note; **phone numbers, long ID numbers and email addresses are removed from messages before they are stored** (flagged "number-removed" for the reviewer), and older messages were cleaned once | Data is stored unencrypted; a voice recording can still contain details a person speaks; names and addresses are not detected | Encrypt the database or use a managed one; restrict who is an admin; tell citizens that voice notes can hold personal details (done in the privacy note) (Medium) |
| 6 | **Information disclosure** to third parties | Voice, text or answers sent to outside services | Off unless a key is set; disclosed in the privacy note; Fulfulde is not sent to speech recognition | Providers may process data outside Nigeria | Keep providers off for the pilot unless needed; review provider terms (Medium) |
| 7 | **Denial of service** | Flooding the app with messages or large audio | 15 messages per hour per session; 10 MB audio limit | A new session resets the limit; free hosting has its own limits | Rate-limit at the host or proxy level and per device; cap daily totals (Medium) |
| 8 | **Elevation of privilege** via the AI | A citizen message that tells the AI draft to ignore its rules ("prompt injection") | The message is treated as untrusted data; the AI sees only confirmed facts; a person edits and publishes every draft | A busy reviewer could trust a bad draft | Show "grounded: no" prominently; never auto-publish (kept) (Low) |
| 9 | **Misuse for persuasion or abuse** | Vote-buying offers, partisan messages, scams | Risk flags (link, vote-buying, rumour, flood-rumour, contact request, partisan) for the reviewer; no persuasion features | Flags are rules, so they miss new wording | Review the flag list weekly during the election period (Medium) |
| 10 | **Wrong or stale information** | A date or address changes after publication | Source and date per fact; election dates re-checked against INEC | Nobody is reminded to re-check | Add a re-verification schedule; link to INEC's official timetable (High) |
| 11 | **USSD/SMS channel** | Sender-ID spoofing; the sender's phone number is personal data | Replies come from a human admin; sender ID "MURYA" | Simulator only; the number is not yet minimised | Store only a one-way hash of the number; register the sender ID; state it in the privacy note (High) |
| 12 | **Platform loss** | Free hosting wipes the database on restart | Admin can export data | No backups | Managed database and scheduled backups (Medium) |

## 3. Residual risk we accept for the prototype

- One reviewer and a small fact base. Human error is possible, so every office address and date shows its source and review state.
- The pilot uses only consenting adults and no real PVC numbers.

## 4. Priority fixes before any live use

1. ~~Admin hash out of the code and a database-based lockout~~ done (delete the old fallback values and set a strong passphrase).
2. ~~Audit log~~ done; individual reviewer accounts still to do.
3. ~~Redaction of phone-like numbers before storing~~ done (voice recordings and free-text names are not covered).
4. Managed database with backups.
5. A registered sender ID and a hashed phone number for USSD/SMS.
6. A re-verification schedule for every fact.

*Last updated: [date]. Owner: Zaharaddeen Muhammad.*

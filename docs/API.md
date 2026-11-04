# MURYA interfaces

Version 1.0 · 3 November 2026. The web app has no public API. This page documents its address options and the USSD/SMS service.

## 1. Web app address options

| Option | Example | Effect |
|---|---|---|
| `page` | `?page=Verified%20Info` | Opens that page: Home, Ask, Verified Info, Polling Units, Learn, Dashboard, Responsible AI, Privacy, Admin, Contact |
| `lang` | `?lang=English` | Sets the language: Hausa, English or Fulfulde |
| `debug` | `?debug=1` | Shows a small line with the session code, start time, page and language |

The page and language are written back to the address as you use the app, so a reload or a dropped connection returns to the same place.

## 2. USSD callback (Africa's Talking)

`POST /murya/<USSD_TOKEN>` with form fields:

| Field | Meaning |
|---|---|
| `phoneNumber` | The caller's number |
| `text` | Everything the caller has typed in this session, joined with `*` |
| `sessionId`, `serviceCode`, `networkCode` | Sent by Africa's Talking (not used) |

**Response:** plain text. It begins `CON ` (show this and wait for input) or `END ` (show this and finish). A wrong or missing token returns 404. Every screen is plain ASCII and at most 182 characters.

**Menu map** (`text` shown for each step):

| `text` | Screen |
|---|---|
| (empty) | Language: 1 English, 2 Hausa |
| `1` or `2` | Main menu: 1 Ask a question, 2 Report a problem |
| `L*1` | Ask menu: 1 Election dates, 2 INEC office in my LGA, 3 Photocopy of my PVC?, 4 How to check my PVC, 5 Something else |
| `L*1*1`, `L*1*3`, `L*1*4` | Verified answer, then end |
| `L*1*2` | LGA list, six per screen; `7` shows the next page; picking a number shows that LGA's office address |
| `L*1*5*<question>` | Stores the question for a reviewer, then ends |
| `L*2` | Report: polling-unit code (e.g. `05-04-02-001`, or `0` if unknown) |
| `L*2*<PU>` | Issue menu: 1 BVAS failure, 2 Late materials, 3 Vote buying, 4 Violence, 5 No EC8A, 6 Other |
| `L*2*<PU>*<issue>*<description>` | Stores the report, then ends |

`L` is the language number. A `*` typed inside a description is kept. Descriptions have numbers and emails removed. At most 5 messages per number per hour.

## 3. Reviewer dashboard (USSD service)

| Route | Method | Purpose |
|---|---|---|
| `/login` | GET, POST | Sign-in page (user name, password). Eight wrong tries lock an address for 5 minutes |
| `/logout` | POST | Sign out |
| `/` and `/dashboard` | GET | Messages and reports, phone numbers masked |
| `/reply` | POST | Send an SMS from the sender name MURYA (needs a form token). Marks the report replied only if Africa's Talking says it was sent |
| `/delete` | POST | Delete one report (needs a form token) |
| `/export` | GET | CSV without phone numbers (short one-way codes instead) |
| `/health` | GET | Returns `ok` for the host's health check |

Everything except `/health` and `/login` needs a signed-in session (12 hours). Pages are marked do-not-index and not cached.

## 4. Settings

See `ARCHITECTURE.md` section 4 for the secrets and environment variables of each service.

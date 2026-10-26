# MURYA — Muryar Zabe | Voice of the Election
**Track 3: Inclusive & Multilingual Electoral/Civic Technology**
**AI4Elections Hackathon 2026-2027 by Rise Networks & Partners**

**Live Demo:** https://murya-engrdeeno.streamlit.app  
**Team:** Bauchi, Bauchi State — Individual Entry  
**Contact:** EngrDeeno

### 1. Problem Statement & Intended Users
In Bauchi State (5.1M voters, 20 LGAs), 40% of voters speak Hausa fluently but struggle to read English INEC notices. Fake news about PVC collection, polling units, and election dates spreads faster on WhatsApp than official info from inec.gov.ng. Rural women, elderly, and low-literacy voters are excluded.

**Intended Users:** Bauchi voters who use WhatsApp voice notes, market women, youth who translate for parents, community radio listeners.

### 2. Solution: MURYA
MURYA is a voice-first, human-approved helpdesk:
- Ask in Hausa by text OR voice (like WhatsApp)
- Auto-detect Hausa vs English
- Listen 🔊 answer with gTTS
- Share verified answer to WhatsApp with one tap
- Dashboard shows aggregates only — no private data

### 3. Methodology & Technical Architecture
**Stack:** Python, Streamlit, SQLite (V3) → Postgres Supabase (V4), gTTS, SpeechRecognition

**Pure Functions (testable offline):**
- `norm(text)` — lowercase, remove Hausa diacritics
- `toks(text)` — tokenize, handle Hausa words
- `kb_match(query, kb, threshold=0.45)` — TF-IDF cosine match to verified KB only from inec.gov.ng
- `risk_flags(text)` — Flags: vote-buying, rumour, partisan, contact-request, link, PVC-request

**Flow:**
User (text/voice) → STT → norm → risk_flags → kb_match (grounded only) → ai_draft (never publishes) → Human reviewer checks inec.gov.ng → Publishes in Admin

**Knowledge Base:** 4 seeded FAQs verified from INEC:
1. How to check PVC collection status
2. Where is my polling unit
3. What is CVR
4. Bauchi 20 LGA INEC offices (V4 addition)

### 4. Evidence of Testing & Evaluation
**Built-in Self-Test: `/Responsible AI` page → Run Evaluation**

- FAQ Retrieval: 9/11 correct (81.8%) — Tested Hausa/English variants: "Yaya zan duba PVC dina?", "Ina polling unit dina?", etc.
- Risk Flags: 6/6 (100%) — Correctly flagged "Zan baka kudi ka zabe ni", "An dage zabe", "Link na PVC"
- Language Detection: Hausa vs English auto-detect via HAUSA_WORDS dictionary

**Honest Limitations:**
- SQLite resets on Streamlit Cloud — Fixed in V4 with Supabase Postgres
- gTTS voice is robotic, not native Hausa elder voice
- STT accuracy drops in noisy market
- No real-time INEC API — manual verification by human
- Fulfulde, Kanuri not yet supported (Bauchi North)

### 5. Responsible AI, Privacy & Security
**Where AI is used:** STT transcription, language detection, KB matching, risk flagging (assistive only)
**Where AI is NEVER used:** AI never publishes answer alone. `ai_grounded=False` if no KB match. Every answer requires human Publish click.

**Privacy by Design:**
- Consent screen before storage
- Warning: "Do not share PVC number, phone number"
- SID anonymous — user sees only own messages
- One-tap `delete_sid()` — deletes all user data
- Dashboard aggregates only, no personal data shown
- Admin password salted hash + purge by age

**Nonpartisan & Safe:**
- Disclaimer everywhere: "Independent civic-tech project. Not an official INEC product. Confirm at inec.gov.ng"
- No partisan persuasion, no microtargeting, no access to live electoral infrastructure — uses only public authorized data per programme rules

### 6. Scalability & Pathway to Product
**V3 → V4 → Product:**
- V3: Streamlit web (current)
- V4-A: Supabase Postgres + 20 LGA addresses + PDF eval report
- V4-B: WhatsApp Cloud API Bot — same brain, same functions, but user sends voice note on WhatsApp (90% of Bauchi uses WhatsApp)
- Future: Offline mode (localStorage cache), Fulfulde/Kanuri, community radio integration

**Cost:** Runs on free tier. Scales to other states by adding LGA dict and Hausa/Yoruba/Igbo dictionaries.

### 7. Demo & Video
Video (2 min): https:// [add YouTube link after upload]
Live: https://murya-engrdeeno.streamlit.app

### 8. Compliance
Team uses only synthetic/public data from inec.gov.ng, voters.inecnigeria.org. No BVAS, no voter register access. Complies with Code of Conduct, Responsible AI, IP rules — IP retained by team per rules.
# Retrieval results

| Method | Clean questions | Typos | Voice-to-text noise | Code-switching | Short / low-literacy | Wrongly answered (should go to a person) |
|---|---|---|---|---|---|---|
| TF-IDF baseline | 32/45 | 27/45 | 33/45 | 9/11 | 3/10 | 3/15 |
| MURYA matcher | 43/45 | 43/45 | 42/45 | 10/11 | 9/10 | 0/15 |

Questions per set: Clean questions 45, Typos 45, Voice-to-text noise 45, Code-switching 11, Short / low-literacy 10; should-go-to-a-person 15.

Answer length for SMS (160 characters) and USSD (182): 6 of 8 FAQ answers fit; longer ones: FAQ 2 Hausa (231 chars), FAQ 2 English (240 chars).

*Questions written by the developer; typo and voice-noise variants were generated automatically from the clean set. A comparison on a small set, not a benchmark. Real-user accuracy is measured in the pilot.*

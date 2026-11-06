"""
Make a SYNTHETIC accessibility-barriers survey for MURYA's own setting: Bauchi's 20 LGAs and MURYA's three languages
(Hausa, Fulfulde, English). Nothing in it is real. Every answer is drawn at random, so it shows NO real pattern.

It has the same columns as the organisers' file (accessibility_barriers_survey_synthetic.csv) plus one extra column, lga,
so the Dashboard can filter by LGA and by language. 25 made-up respondents per LGA, 500 in all.

Run (VS Code: Terminal > New Terminal, in the folder that holds this file):
    python make_synthetic_barriers_bauchi.py
It writes accessibility_barriers_survey_synthetic_bauchi.csv. Put it in the data folder next to app.py.
"""
import csv
import random

random.seed(2027)   # same file every time
LGAS = ["Alkaleri", "Bauchi (Kofar Ran)", "Bogoro", "Dambam", "Darazo", "Dass", "Gamawa", "Ganjuwa", "Giade", "Itas/Gadau",
        "Jama'are", "Katagum", "Kirfi", "Misau", "Ningi", "Shira", "Tafawa Balewa", "Toro", "Warji", "Zaki"]
# Choices and rough shares follow the organisers' file. The shares are arbitrary: this is made-up data.
CHOICES = {
    "settlement": (["urban", "rural"], [50, 50]),
    "age_band": (["18-24", "25-34", "35-49", "50-64", "65+"], [20, 19, 17, 26, 18]),
    "gender": (["male", "female", "undisclosed"], [38, 32, 30]),
    "disability_type": (["none", "mobility", "visual", "hearing", "cognitive", "multiple"], [60, 11, 9, 8, 7, 5]),
    "preferred_language": (["ha", "ff", "en"], [60, 20, 20]),
    "main_barrier": (["distance", "physical_access", "no_braille_or_large_print", "no_id_documents", "language",
                      "safety_concerns", "none", "information_gap"], [15, 15, 12, 12, 12, 12, 11, 11]),
}
rows, n = [], 0
for lga in LGAS:
    for _ in range(25):
        n += 1
        pick = {k: random.choices(v[0], v[1])[0] for k, v in CHOICES.items()}
        rows.append([f"BAU-{n:04d}", "Bauchi", lga, pick["settlement"], pick["age_band"], pick["gender"], pick["disability_type"],
                     pick["preferred_language"], pick["main_barrier"], random.random() < 0.58, random.randint(1, 5)])

out = "accessibility_barriers_survey_synthetic_bauchi.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["resp_id", "state", "lga", "settlement", "age_band", "gender", "disability_type", "preferred_language",
                "main_barrier", "voted_last_cycle_simulated", "confidence_finding_info_1_5"])
    w.writerows(rows)
print(f"Wrote {len(rows)} SYNTHETIC respondents in {len(LGAS)} LGAs to {out}")
print("Every answer is random. It shows no real pattern and says nothing about real Bauchi voters.")

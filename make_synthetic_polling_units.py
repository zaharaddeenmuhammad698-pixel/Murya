"""
Make a SYNTHETIC polling-unit list for the MURYA demo. Nothing in it is real.

The programme asks teams to use synthetic data instead of INEC's real polling-unit list. If the organisers' own file
(polling_units_synthetic.csv in their repository) fits, use that one. This script is a fallback.

What it makes: the 20 real Bauchi LGA names, but made-up wards and polling units, all named SAMPLE, with codes that start
with 00 (no real INEC state uses 00), so none of it can be mistaken for a real polling unit.

Run (VS Code: Terminal > New Terminal, in the folder that holds this file):
    python make_synthetic_polling_units.py
It writes polling_units_synthetic_bauchi.csv with the columns lga, ward, pu_code, pu_name.
Import it in the app: Admin > Polling units, tick "This list is SYNTHETIC", choose the file, press Import.
"""
import csv
import random

random.seed(2027)   # same file every time
LGAS = ["Alkaleri", "Bauchi (Kofar Ran)", "Bogoro", "Dambam", "Darazo", "Dass", "Gamawa", "Ganjuwa", "Giade", "Itas/Gadau",
        "Jama'are", "Katagum", "Kirfi", "Misau", "Ningi", "Shira", "Tafawa Balewa", "Toro", "Warji", "Zaki"]
KINDS = ["Primary School", "Market Square", "Health Centre", "Town Hall", "Community Centre", "Open Space"]

rows = []
for li, lga in enumerate(LGAS, 1):
    for wi in range(1, random.randint(8, 12) + 1):
        for pi in range(1, random.randint(4, 9) + 1):
            rows.append((lga, f"SAMPLE Ward {wi:02d}", f"00-{li:02d}-{wi:02d}-{pi:03d}", f"SAMPLE {random.choice(KINDS)} {pi:03d}"))

out = "polling_units_synthetic_bauchi.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["lga", "ward", "pu_code", "pu_name"])
    w.writerows(rows)
print(f"Wrote {len(rows)} SYNTHETIC polling units in {len(LGAS)} LGAs to {out}")
print("Every ward and unit is named SAMPLE and every code starts with 00. None of it is real.")

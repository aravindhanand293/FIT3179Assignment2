"""Build the CSV files for the drought charts.

Reads the Bureau of Meteorology yearly files saved in data-prep/bom/
(rain_<region>.txt and tmean_<region>.txt for aus, nsw, vic, qld, sa, wa, tas, nt)
and, if it exists, the SILO grid CSV made by silo_to_csv.py.

Writes to data/:
  state_annual.csv   one row per state per year (charts A, E, F, H, I)
  aus_annual.csv     one row per year for all of Australia (charts B, G, J)
  drought_runs.csv   every run of 3+ below-average years in a row (chart D)
  waffle_2017_2019.csv  100 squares for the waffle chart (chart C)

Run from the top folder of your repo:  python3 data-prep/build_chart_data.py
Uses only Python's standard library.
"""
import csv
import math
import os

BOM_DIR = "data-prep/bom"
OUT_DIR = "data"
REGIONS = {  # file code: (name used on the page, short label)
    "nsw": ("New South Wales", "NSW"),
    "vic": ("Victoria", "VIC"),
    "qld": ("Queensland", "QLD"),
    "sa": ("South Australia", "SA"),
    "wa": ("Western Australia", "WA"),
    "tas": ("Tasmania", "TAS"),
    "nt": ("Northern Territory", "NT"),
}
NORMAL = (1961, 1990)   # the same "normal" as the maps
MIN_RUN = 3             # a drought run = at least 3 below-average years in a row


def read_bom(path):
    """Return {year: value} from a BoM 'Raw dataset' text file."""
    values = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and len(parts[0]) == 12:
                values[int(parts[0][:4])] = float(parts[1])
    return values


def rain_and_temp(code):
    """Return a list of rows (year, rain_mm, rain_pct, temp_anom) for one region."""
    rain = read_bom(os.path.join(BOM_DIR, f"rain_{code}.txt"))
    temp = read_bom(os.path.join(BOM_DIR, f"tmean_{code}.txt"))
    normal_years = range(NORMAL[0], NORMAL[1] + 1)
    normal = sum(rain[y] for y in normal_years) / len(normal_years)
    rows = []
    for year in sorted(rain):
        rows.append({
            "year": year,
            "rain_mm": round(rain[year], 1),
            "rain_pct": round(rain[year] / normal * 100, 1),
            "temp_anom": temp.get(year, ""),   # blank before 1910
        })
    return rows


def write_csv(name, rows):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):>5} rows to {path}")


os.makedirs(OUT_DIR, exist_ok=True)

# 1. One row per state per year, and every drought run
state_rows, runs = [], []
for code, (state, abbrev) in REGIONS.items():
    rows = rain_and_temp(code)
    for r in rows:
        state_rows.append({"state": state, "abbrev": abbrev, **r})

    run = []
    for r in rows + [{"year": None, "rain_pct": 999}]:   # the extra row closes the last run
        if r["rain_pct"] < 100:
            run.append(r)
            continue
        if len(run) >= MIN_RUN:
            runs.append({
                "state": state,
                "abbrev": abbrev,
                "start": run[0]["year"],
                "end": run[-1]["year"],
                "years": len(run),
                "mean_pct": round(sum(x["rain_pct"] for x in run) / len(run), 1),
            })
        run = []

write_csv("state_annual.csv", state_rows)
write_csv("drought_runs.csv", runs)

# 2. All of Australia
write_csv("aus_annual.csv", rain_and_temp("aus"))

# 3. Waffle: share of Australia's land in each rainfall band, 2017-2019
grid_path = os.path.join(OUT_DIR, "rain_grid_2017_2019.csv")
if os.path.exists(grid_path):
    bands = [  # (label, lower limit) in the same bands as the maps
        ("Under 60%", -1), ("60–80%", 60), ("80–95%", 80),
        ("95–105%", 95), ("105–120%", 105), ("120% or more", 120),
    ]
    area = {label: 0.0 for label, _ in bands}
    with open(grid_path) as f:
        for p in csv.DictReader(f):
            value = float(p["value"])
            label = [b for b, lower in bands if value >= lower][-1]
            # grid squares get smaller towards the south, so weight by latitude
            area[label] += math.cos(math.radians(float(p["lat"])))
    total = sum(area.values())
    exact = {b: area[b] / total * 100 for b in area}
    squares = {b: int(exact[b]) for b in exact}
    # hand out the squares lost to rounding down, largest remainder first
    for b in sorted(exact, key=lambda b: exact[b] - squares[b], reverse=True)[: 100 - sum(squares.values())]:
        squares[b] += 1
    waffle, i = [], 0
    for order, (label, _) in enumerate(bands):
        for _ in range(squares[label]):
            waffle.append({"id": i, "col": i % 10, "row": i // 10, "band": label,
                           "band_order": order, "pct_of_land": round(exact[label], 1)})
            i += 1
    write_csv("waffle_2017_2019.csv", waffle)
else:
    print(f"Skipped the waffle: {grid_path} not found (run silo_to_csv.py first)")
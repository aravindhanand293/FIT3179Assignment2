"""Build the bin map data from SILO gridded rainfall.

Downloads SILO monthly rainfall (one NetCDF file per year, about 14 MB each),
works out each grid cell's 2017-2019 rainfall as a % of its 1961-1990 average,
and writes data/rain_grid_2017_2019.csv with columns lon, lat, value.

Setup (once):   pip3 install xarray netCDF4
Run:            python3 silo_to_csv.py

Source: SILO, Queensland Government, CC BY 4.0
https://www.longpaddock.qld.gov.au/silo/gridded-data/
"""
import os
import urllib.request

import xarray as xr

URL = "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/monthly_rain/{year}.monthly_rain.nc"
BASELINE_YEARS = range(1961, 1991)   # 1961-1990, the same "normal" as your other maps
DROUGHT_YEARS = range(2017, 2020)    # 2017-2019, the Tinderbox Drought
COARSEN = 5                          # 5 x 0.05 degrees = 0.25 degree points
DOWNLOAD_DIR = "silo_downloads"      # keep this folder out of your repo
OUT = "data/rain_grid_2017_2019.csv"


def annual_total(year):
    """Download one year (if not already downloaded) and return its rainfall total grid in mm."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    path = os.path.join(DOWNLOAD_DIR, f"{year}.monthly_rain.nc")
    if not os.path.exists(path):
        print(f"Downloading {year} ...")
        urllib.request.urlretrieve(URL.format(year=year), path)
    with xr.open_dataset(path) as ds:
        # add up the 12 months; ocean cells have no data and stay empty
        return ds["monthly_rain"].sum("time", min_count=12).load()


# Average yearly rainfall over the baseline and over the drought
baseline = sum(annual_total(y) for y in BASELINE_YEARS) / len(BASELINE_YEARS)
drought = sum(annual_total(y) for y in DROUGHT_YEARS) / len(DROUGHT_YEARS)

# Drought rainfall as a % of normal, then average 5 x 5 blocks into 0.25 degree points
pct = (drought / baseline * 100).where(baseline > 0)
pct = pct.coarsen(lat=COARSEN, lon=COARSEN, boundary="trim").mean()

table = pct.rename("value").to_dataframe().reset_index()[["lon", "lat", "value"]]
table = table.dropna()
table["lon"] = table["lon"].round(3)
table["lat"] = table["lat"].round(3)
table["value"] = table["value"].round(1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
table.to_csv(OUT, index=False)
print(f"Wrote {len(table)} points to {OUT}")
print(table["value"].describe().round(1))
import json
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import pandas as pd
import requests

from utils import prep
from utils.config import (
    DATA_DIR,
    GEO_FILE,
    GEO_URL,
    METROPOLE_CODES,
    MONTHLY_FILE,
    ODRE_URL,
    QUALITY_FILE,
    RAW_COLUMNS,
    REGION_CODES,
)


def expected_rows(code):
    url = ODRE_URL.replace("/exports/csv", "/records")
    params = {"limit": 0, "where": f"code_insee_region='{code}'"}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    return response.json()["total_count"]


def fetch_region(code, retries=3):
    params = {"select": ",".join(RAW_COLUMNS), "where": f"code_insee_region='{code}'"}
    for attempt in range(retries):
        try:
            response = requests.get(ODRE_URL, params=params, timeout=600)
            response.raise_for_status()
            df = pd.read_csv(BytesIO(response.content), sep=";", dtype={"code_insee_region": str}, low_memory=False)
            if len(df) != expected_rows(code):
                raise requests.RequestException(f"incomplete download for region {code}")
            return df
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(5)


def fetch_geojson():
    geo = requests.get(GEO_URL, timeout=120).json()
    geo["features"] = [f for f in geo["features"] if f["properties"]["reg"] in METROPOLE_CODES]
    return geo


def fetch_and_cache(force=False):
    if not force and MONTHLY_FILE.exists() and QUALITY_FILE.exists() and GEO_FILE.exists():
        return
    DATA_DIR.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        raws = list(pool.map(fetch_region, REGION_CODES))
    monthly, stats = [], []
    for raw in raws:
        clean, region_stats = prep.clean_raw(raw)
        monthly.append(prep.to_monthly(clean))
        stats.append(region_stats)
    pd.concat(monthly).round(3).to_csv(MONTHLY_FILE, index=False)
    pd.DataFrame(stats).to_csv(QUALITY_FILE, index=False)
    GEO_FILE.write_text(json.dumps(fetch_geojson()), encoding="utf-8")


def load_data():
    fetch_and_cache()
    monthly = pd.read_csv(MONTHLY_FILE, dtype={"region_code": str}, parse_dates=["month"])
    quality = pd.read_csv(QUALITY_FILE, dtype={"region_code": str})
    geojson = json.loads(GEO_FILE.read_text(encoding="utf-8"))
    return monthly, quality, geojson

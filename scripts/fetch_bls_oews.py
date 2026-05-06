"""
Fetch BLS OEWS metropolitan-area data and extract AI-relevant occupations.

AI-relevant SOC codes used:
  - 15-1221  Computer and Information Research Scientists (closest to AI/ML researchers)
  - 15-2051  Data Scientists (highly AI-relevant)

Output: outputs/ai_hub_data/usa_ai_employment_by_msa.csv
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

OEWS_URL = "https://www.bls.gov/oes/special-requests/oesm25ma.zip"
OEWS_URL_FALLBACK = "https://www.bls.gov/oes/special-requests/oesm24ma.zip"
AI_SOC_CODES = {"15-1221", "15-2051"}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_oews():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ai-hub-analysis/1.0)"}
    for url in (OEWS_URL, OEWS_URL_FALLBACK):
        print(f"Trying: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=120)
            if resp.status_code == 200 and resp.content[:2] == b"PK":
                print(f"Downloaded {len(resp.content) / 1024 / 1024:.1f} MB from {url}")
                return resp.content, url
            else:
                print(f"  status={resp.status_code}, not a zip")
        except Exception as e:
            print(f"  error: {e}")
    raise RuntimeError("All OEWS URLs failed")


def extract_metro_table(zip_bytes):
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    for name in z.namelist():
        print(f"  zip member: {name}")
        if name.lower().endswith(".xlsx") and "ma" in name.lower() and "msa" in name.lower():
            print(f"  using: {name}")
            with z.open(name) as f:
                return pd.read_excel(f, dtype=str)
    for name in z.namelist():
        if name.lower().endswith(".xlsx"):
            print(f"  fallback xlsx: {name}")
            with z.open(name) as f:
                return pd.read_excel(f, dtype=str)
    raise RuntimeError("No xlsx file found in OEWS zip")


def main():
    # Try 2025 cache first, then 2024
    cache_25 = OUTPUT_DIR / "oesm25ma.zip"
    cache_24 = OUTPUT_DIR / "oesm24ma.zip"
    if cache_25.exists():
        print(f"Using cached 2025: {cache_25}")
        zip_bytes = cache_25.read_bytes()
        used_url = "cached oesm25ma.zip"
    elif cache_24.exists() and not cache_25.exists():
        # Try fresh 2025 download; only fall back to cached 2024 if 2025 download fails
        try:
            zip_bytes, used_url = download_oews()
            target_cache = cache_25 if "oesm25ma" in used_url else cache_24
            target_cache.write_bytes(zip_bytes)
            print(f"Cached to: {target_cache}")
        except RuntimeError:
            print(f"Falling back to cached 2024: {cache_24}")
            zip_bytes = cache_24.read_bytes()
            used_url = "cached oesm24ma.zip"
    else:
        zip_bytes, used_url = download_oews()
        target_cache = cache_25 if "oesm25ma" in used_url else cache_24
        target_cache.write_bytes(zip_bytes)
        print(f"Cached to: {target_cache}")
    print(f"Source: {used_url}")

    df = extract_metro_table(zip_bytes)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} cols")
    print("Columns:", list(df.columns))

    # Standardize column names
    df.columns = [c.lower().strip() for c in df.columns]

    soc_col = next((c for c in df.columns if "occ_code" in c or c == "occ code"), None)
    area_col = next((c for c in df.columns if c == "area" or c.startswith("area_")), None)
    title_col = next((c for c in df.columns if "occ_title" in c or "occ title" in c), None)
    area_title_col = next((c for c in df.columns if "area_title" in c or "area title" in c), None)
    emp_col = next((c for c in df.columns if c == "tot_emp" or c == "tot emp"), None)
    print(f"  soc={soc_col}  area={area_col}  area_title={area_title_col}  occ_title={title_col}  emp={emp_col}")

    if not all([soc_col, area_title_col, emp_col]):
        print("ERROR: required columns missing")
        sys.exit(1)

    df = df[[soc_col, area_title_col, title_col, emp_col]].copy()
    df.columns = ["soc", "area", "title", "emp"]
    df["soc"] = df["soc"].astype(str).str.strip()
    df["emp_num"] = pd.to_numeric(df["emp"].astype(str).str.replace(",", "").str.replace("**", ""), errors="coerce")

    # Filter to AI-relevant SOCs
    ai = df[df["soc"].isin(AI_SOC_CODES)].copy()
    print(f"AI rows: {len(ai)}")

    # Aggregate by metro: sum employment across the AI SOCs
    agg = ai.groupby("area", as_index=False)["emp_num"].sum().rename(columns={"emp_num": "ai_emp"})

    # Get total MSA employment from row "00-0000 All Occupations"
    totals = df[df["soc"] == "00-0000"].copy()
    totals = totals.groupby("area", as_index=False)["emp_num"].sum().rename(columns={"emp_num": "total_emp"})

    merged = agg.merge(totals, on="area", how="left")
    merged["ai_per_1000"] = merged["ai_emp"] / merged["total_emp"] * 1000
    merged = merged.sort_values("ai_per_1000", ascending=False)

    out = OUTPUT_DIR / "usa_ai_employment_by_msa.csv"
    merged.to_csv(out, index=False)
    print(f"\nWrote {len(merged)} MSA rows to {out}")
    print("\nTop 20 by AI concentration (per 1,000 workers):")
    print(merged.head(20).to_string(index=False))
    print("\nTop 20 by absolute AI employment:")
    print(merged.sort_values("ai_emp", ascending=False).head(20).to_string(index=False))


if __name__ == "__main__":
    main()

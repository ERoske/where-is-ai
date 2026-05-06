"""
Fetch AI research output by city from OpenAlex (free, no auth).

Pulls works in concept "Artificial Intelligence" from the last ~12 months,
groups by author institution country/city, returns top cities globally.

Output: outputs/ai_hub_data/world_ai_research_by_city.csv
"""
import csv
import json
import time
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# OpenAlex Concept IDs
# C154945302 = Artificial Intelligence (top-level concept)
# C119857082 = Machine Learning
AI_CONCEPT = "C154945302"

# Window: last 12 months from today
FROM_DATE = "2025-05-06"
TO_DATE = "2026-05-06"

UA = "asking-good-questions/1.0 (mailto:edward@dawnwardpr.com)"


def fetch_institutions_top_authors():
    """
    Pull top institutions globally by AI/ML works in the last 12 months.
    Use OpenAlex's group_by feature for institutions on the works endpoint.
    """
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"concepts.id:{AI_CONCEPT},from_publication_date:{FROM_DATE},to_publication_date:{TO_DATE}",
        "group_by": "authorships.institutions.id",
        "per_page": "200",
        "mailto": "edward@dawnwardpr.com",
    }
    print(f"Calling OpenAlex group_by institutions...")
    resp = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    print(f"Got {len(data.get('group_by', []))} institutions in top group")
    return data.get("group_by", [])


def fetch_institution_metadata(inst_id):
    """Fetch a single institution's location info (city, country)."""
    short = inst_id.split("/")[-1] if inst_id else None
    if not short:
        return None
    url = f"https://api.openalex.org/institutions/{short}"
    try:
        resp = requests.get(url, params={"mailto": "edward@dawnwardpr.com"}, headers={"User-Agent": UA}, timeout=30)
        if resp.status_code != 200:
            return None
        d = resp.json()
        geo = d.get("geo") or {}
        return {
            "id": d.get("id"),
            "display_name": d.get("display_name"),
            "country": geo.get("country"),
            "country_code": geo.get("country_code"),
            "city": geo.get("city"),
            "region": geo.get("region"),
            "lat": geo.get("latitude"),
            "lon": geo.get("longitude"),
            "type": d.get("type"),
            "homepage": d.get("homepage_url"),
        }
    except Exception as e:
        print(f"  err on {inst_id}: {e}")
        return None


def main():
    institutions = fetch_institutions_top_authors()
    if not institutions:
        print("ERROR: no institutions returned")
        return

    # Take top 200 institutions by AI publications
    rows = []
    for i, inst in enumerate(institutions[:200]):
        inst_id = inst.get("key")
        ai_works = inst.get("count")
        display = inst.get("key_display_name") or "?"
        print(f"  {i+1:3d}. {display[:60]:60s}  AI works: {ai_works:>5}")
        meta = fetch_institution_metadata(inst_id)
        if meta and meta.get("city") and meta.get("lat"):
            rows.append({
                "institution_id": inst_id,
                "institution": display,
                "ai_works": ai_works,
                "city": meta["city"],
                "country": meta["country"],
                "country_code": meta["country_code"],
                "region": meta["region"],
                "lat": meta["lat"],
                "lon": meta["lon"],
                "type": meta["type"],
            })
        time.sleep(0.05)  # polite

    # Save institution-level data
    inst_path = DATA_DIR / "world_ai_research_by_institution.csv"
    with inst_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["institution_id", "institution", "ai_works", "city", "country", "country_code", "region", "lat", "lon", "type"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {len(rows)} institutions to {inst_path}")

    # Aggregate by city
    city_agg = {}
    for r in rows:
        key = (r["city"], r["country_code"])
        if key not in city_agg:
            city_agg[key] = {
                "city": r["city"],
                "country": r["country"],
                "country_code": r["country_code"],
                "ai_works": 0,
                "institutions": 0,
                "lat": r["lat"],
                "lon": r["lon"],
                "top_institution": r["institution"],
                "top_institution_works": r["ai_works"],
            }
        city_agg[key]["ai_works"] += r["ai_works"]
        city_agg[key]["institutions"] += 1
        if r["ai_works"] > city_agg[key]["top_institution_works"]:
            city_agg[key]["top_institution"] = r["institution"]
            city_agg[key]["top_institution_works"] = r["ai_works"]

    city_rows = sorted(city_agg.values(), key=lambda x: -x["ai_works"])

    city_path = DATA_DIR / "world_ai_research_by_city.csv"
    with city_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["city", "country", "country_code", "ai_works", "institutions", "lat", "lon", "top_institution", "top_institution_works"])
        w.writeheader()
        w.writerows(city_rows)
    print(f"Saved {len(city_rows)} cities to {city_path}")

    print("\nTop 25 cities by AI publication output (last 12 months):")
    for i, r in enumerate(city_rows[:25]):
        print(f"  {i+1:2d}. {r['city']:25s} {r['country_code']:3s}  works={r['ai_works']:>6}  insts={r['institutions']:>2}  top: {r['top_institution'][:50]}")


if __name__ == "__main__":
    main()

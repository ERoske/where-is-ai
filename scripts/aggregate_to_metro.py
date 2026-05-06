"""
Aggregate institution-level world data to METRO level.

Uses a hand-curated city -> metro mapping. Most cities pass through unchanged
(Beijing, Paris, Singapore, etc. are already metro-coherent in OpenAlex's tagging).
A small number of fragmented cases get explicitly grouped:

  - U.S. Bay Area: Stanford, Mountain View, Berkeley, San Francisco, San Jose,
    Palo Alto, Sunnyvale, Cupertino aggregate to "San Francisco-San Jose Bay Area"
    (matches U.S. Census CSA #488).
  - U.S. Boston Metro: Cambridge, Boston, Needham aggregate to
    "Boston-Cambridge-Newton Metro" (matches U.S. Census MSA #14460).
  - Hong Kong: Hong Kong + Pok Fu Lam aggregate to "Hong Kong" (Pok Fu Lam is a
    district of Hong Kong).

For more rigorous global aggregation in future, swap this for a join against the
GHSL Urban Centre Database (https://ghsl.jrc.ec.europa.eu/ghs_stat_ucdb2015mt_r2019a.php).

Outputs: data/world_ai_research_by_metro.csv
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# (city, country_code) -> (metro_name, metro_country, metro_lat, metro_lon)
# Cities not in this dict are passed through with their original (city, country, lat, lon).
CITY_TO_METRO = {
    # U.S. San Francisco-San Jose Bay Area (CSA)
    ("Stanford", "US"):       ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Mountain View", "US"):  ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Berkeley", "US"):       ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("San Francisco", "US"):  ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("San Jose", "US"):       ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Palo Alto", "US"):      ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Sunnyvale", "US"):      ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Cupertino", "US"):      ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Menlo Park", "US"):     ("SF-San Jose Bay Area", "United States", 37.55, -122.10),
    ("Oakland", "US"):        ("SF-San Jose Bay Area", "United States", 37.55, -122.10),

    # U.S. Boston-Cambridge-Newton Metro (MSA)
    ("Cambridge", "US"):      ("Boston Metro", "United States", 42.36, -71.06),
    ("Boston", "US"):         ("Boston Metro", "United States", 42.36, -71.06),
    ("Needham", "US"):        ("Boston Metro", "United States", 42.36, -71.06),
    ("Waltham", "US"):        ("Boston Metro", "United States", 42.36, -71.06),

    # Hong Kong (Pok Fu Lam is a district)
    ("Pok Fu Lam", "HK"):     ("Hong Kong", "Hong Kong", 22.28, 114.17),
    ("Hong Kong", "HK"):      ("Hong Kong", "Hong Kong", 22.28, 114.17),
}


def main():
    df = pd.read_csv(DATA_DIR / "world_ai_research_by_institution.csv")
    print(f"Loaded {len(df)} institutions")

    def map_metro(row):
        key = (row["city"], row["country_code"])
        if key in CITY_TO_METRO:
            metro_name, metro_country, metro_lat, metro_lon = CITY_TO_METRO[key]
            return pd.Series({
                "metro": metro_name,
                "metro_country": metro_country,
                "metro_country_code": row["country_code"],
                "metro_lat": metro_lat,
                "metro_lon": metro_lon,
            })
        # Default: city becomes its own metro
        return pd.Series({
            "metro": row["city"],
            "metro_country": row["country"],
            "metro_country_code": row["country_code"],
            "metro_lat": row["lat"],
            "metro_lon": row["lon"],
        })

    df = pd.concat([df, df.apply(map_metro, axis=1)], axis=1)

    # Aggregate to metro level (group by metro NAME only — lat/lon vary per institution
    # within the same metro and would fragment the grouping; we take a representative
    # lat/lon per metro afterward).
    agg = (
        df.groupby(["metro", "metro_country", "metro_country_code"], as_index=False)
        .agg(
            ai_works=("ai_works", "sum"),
            institutions=("institution", "count"),
            metro_lat=("metro_lat", "first"),
            metro_lon=("metro_lon", "first"),
        )
    )

    # Top institution per metro: sort then take first
    top_inst = (
        df.sort_values("ai_works", ascending=False)
        .groupby("metro", as_index=False)
        .first()[["metro", "institution", "ai_works"]]
        .rename(columns={"institution": "top_institution", "ai_works": "top_institution_works"})
    )
    agg = agg.merge(top_inst, on="metro", how="left")

    # Rename for downstream compatibility (existing render scripts expect "city" column name)
    agg = agg.rename(columns={
        "metro": "city",
        "metro_country": "country",
        "metro_country_code": "country_code",
        "metro_lat": "lat",
        "metro_lon": "lon",
    })

    agg = agg.sort_values("ai_works", ascending=False)

    out = DATA_DIR / "world_ai_research_by_metro.csv"
    agg.to_csv(out, index=False)
    print(f"\nSaved {len(agg)} metros to {out}")

    print("\nTop 25 by AI papers (METRO level):")
    for i, r in agg.head(25).reset_index(drop=True).iterrows():
        print(f"  {i+1:2d}. {r['city']:30s} {r['country_code']:3s}  works={r['ai_works']:>6}  insts={r['institutions']:>2}  top: {r['top_institution'][:50]}")


if __name__ == "__main__":
    main()

"""
Compute year-over-year diff between BLS OEWS 2024 and 2025 metro-level AI employment.

Requires both data/oesm24ma.zip and data/oesm25ma.zip to be present in cache.
Produces:
  - data/usa_ai_employment_yoy.csv   (2024 vs 2025 by MSA + delta + pct change)
  - data/usa_yoy_findings.md         (top movers narrative)

Run AFTER fetch_bls_oews.py has cached both years.
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AI_SOC_CODES = {"15-1221", "15-2051"}


def load_year(year_suffix):
    cache = DATA_DIR / f"oesm{year_suffix}ma.zip"
    if not cache.exists():
        print(f"MISSING: {cache}")
        return None
    z = zipfile.ZipFile(cache)
    target = next(
        (n for n in z.namelist() if n.lower().endswith(".xlsx") and "msa" in n.lower()),
        None,
    )
    if target is None:
        print(f"No MSA xlsx found in {cache}")
        return None
    with z.open(target) as f:
        df = pd.read_excel(f, dtype=str)
    df.columns = [c.lower().strip() for c in df.columns]

    df["soc"] = df["occ_code"].astype(str).str.strip()
    df["emp_num"] = pd.to_numeric(
        df["tot_emp"].astype(str).str.replace(",", "").str.replace("**", ""),
        errors="coerce",
    )

    ai = df[df["soc"].isin(AI_SOC_CODES)].copy()
    agg = ai.groupby("area_title", as_index=False)["emp_num"].sum().rename(columns={"emp_num": f"ai_emp_{year_suffix}"})

    totals = df[df["soc"] == "00-0000"].copy()
    totals = (
        totals.groupby("area_title", as_index=False)["emp_num"]
        .sum()
        .rename(columns={"emp_num": f"total_emp_{year_suffix}"})
    )

    out = agg.merge(totals, on="area_title", how="left")
    out[f"ai_per_1000_{year_suffix}"] = out[f"ai_emp_{year_suffix}"] / out[f"total_emp_{year_suffix}"] * 1000
    return out


def main():
    df_24 = load_year("24")
    df_25 = load_year("25")

    if df_24 is None or df_25 is None:
        print("\nERROR: need both 2024 and 2025 BLS bulk files in data/.")
        print("Run fetch_bls_oews.py once after BLS publishes May 2025 (scheduled 2026-05-15).")
        sys.exit(1)

    merged = df_24.merge(df_25, on="area_title", how="outer")
    merged["delta_emp"] = merged["ai_emp_25"] - merged["ai_emp_24"]
    merged["pct_change_emp"] = merged["delta_emp"] / merged["ai_emp_24"] * 100
    merged["delta_per_1000"] = merged["ai_per_1000_25"] - merged["ai_per_1000_24"]

    merged = merged.sort_values("ai_emp_25", ascending=False)
    out_path = DATA_DIR / "usa_ai_employment_yoy.csv"
    merged.to_csv(out_path, index=False)
    print(f"Wrote {len(merged)} MSAs to {out_path}")

    big_winners = merged.dropna(subset=["delta_emp"]).nlargest(15, "delta_emp")
    big_losers = merged.dropna(subset=["delta_emp"]).nsmallest(15, "delta_emp")
    fastest_growers = merged.dropna(subset=["pct_change_emp"]).nlargest(15, "pct_change_emp")

    findings = DATA_DIR / "usa_yoy_findings.md"
    lines = ["# USA AI Employment Year-Over-Year (May 2024 vs May 2025)\n\n"]
    lines.append("**Data**: BLS OEWS, May 2024 release (April 2, 2025) vs May 2025 release (May 15, 2026).\n")
    lines.append("**SOCs**: 15-1221 (Computer and Information Research Scientists) + 15-2051 (Data Scientists).\n\n")

    lines.append("## Biggest absolute gainers (most AI workers added)\n")
    lines.append("| # | Metro | 2024 | 2025 | Δ workers | Δ % |\n|---|---|---|---|---|---|\n")
    for i, r in big_winners.reset_index(drop=True).iterrows():
        lines.append(
            f"| {i+1} | {r['area_title']} | {int(r['ai_emp_24']):,} | {int(r['ai_emp_25']):,} | +{int(r['delta_emp']):,} | {r['pct_change_emp']:+.1f}% |\n"
        )

    lines.append("\n## Biggest absolute losers\n")
    lines.append("| # | Metro | 2024 | 2025 | Δ workers | Δ % |\n|---|---|---|---|---|---|\n")
    for i, r in big_losers.reset_index(drop=True).iterrows():
        lines.append(
            f"| {i+1} | {r['area_title']} | {int(r['ai_emp_24']):,} | {int(r['ai_emp_25']):,} | {int(r['delta_emp']):,} | {r['pct_change_emp']:+.1f}% |\n"
        )

    lines.append("\n## Fastest growers by percentage (min 100 workers in 2024)\n")
    lines.append("| # | Metro | 2024 | 2025 | Δ % |\n|---|---|---|---|---|\n")
    fg = fastest_growers[fastest_growers["ai_emp_24"] >= 100]
    for i, r in fg.reset_index(drop=True).iterrows():
        lines.append(
            f"| {i+1} | {r['area_title']} | {int(r['ai_emp_24']):,} | {int(r['ai_emp_25']):,} | {r['pct_change_emp']:+.1f}% |\n"
        )

    findings.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote findings to {findings}")
    print("\nTop 5 absolute gainers:")
    print(big_winners[["area_title", "ai_emp_24", "ai_emp_25", "delta_emp", "pct_change_emp"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()

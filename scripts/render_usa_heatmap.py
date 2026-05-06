"""
Render the USA AI hub heatmap from BLS OEWS data.
Uses plotly scatter_geo with dark template.
"""
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "images" / "Heatmap-USA-AI-Jobs.png"

# MSA -> (display label, lat, lon)
# Approximate coordinates for the top metros from BLS data
MSA_COORDS = {
    "New York-Newark-Jersey City, NY-NJ": ("New York", 40.7128, -74.0060),
    "Washington-Arlington-Alexandria, DC-VA-MD-WV": ("Washington DC", 38.9072, -77.0369),
    "San Francisco-Oakland-Fremont, CA": ("San Francisco", 37.7749, -122.4194),
    "Los Angeles-Long Beach-Anaheim, CA": ("Los Angeles", 34.0522, -118.2437),
    "Boston-Cambridge-Newton, MA-NH": ("Boston", 42.3601, -71.0589),
    "Dallas-Fort Worth-Arlington, TX": ("Dallas", 32.7767, -96.7970),
    "San Jose-Sunnyvale-Santa Clara, CA": ("San Jose", 37.3382, -121.8863),
    "Seattle-Tacoma-Bellevue, WA": ("Seattle", 47.6062, -122.3321),
    "Chicago-Naperville-Elgin, IL-IN": ("Chicago", 41.8781, -87.6298),
    "Atlanta-Sandy Springs-Roswell, GA": ("Atlanta", 33.7490, -84.3880),
    "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": ("Philadelphia", 39.9526, -75.1652),
    "Houston-Pasadena-The Woodlands, TX": ("Houston", 29.7604, -95.3698),
    "Denver-Aurora-Centennial, CO": ("Denver", 39.7392, -104.9903),
    "San Diego-Chula Vista-Carlsbad, CA": ("San Diego", 32.7157, -117.1611),
    "Charlotte-Concord-Gastonia, NC-SC": ("Charlotte", 35.2271, -80.8431),
    "Austin-Round Rock-San Marcos, TX": ("Austin", 30.2672, -97.7431),
    "Phoenix-Mesa-Chandler, AZ": ("Phoenix", 33.4484, -112.0740),
    "Detroit-Warren-Dearborn, MI": ("Detroit", 42.3314, -83.0458),
    "Minneapolis-St. Paul-Bloomington, MN-WI": ("Minneapolis", 44.9778, -93.2650),
    "St. Louis, MO-IL": ("St. Louis", 38.6270, -90.1994),
    "Durham-Chapel Hill, NC": ("Research Triangle", 35.9940, -78.8986),
    "Boulder, CO": ("Boulder", 40.0150, -105.2705),
    "Huntsville, AL": ("Huntsville", 34.7304, -86.5861),
    "Lexington Park, MD": ("Pax River MD", 38.2670, -76.4505),
    "Provo-Orem-Lehi, UT": ("Provo", 40.2338, -111.6585),
    "Pittsburgh, PA": ("Pittsburgh", 40.4406, -79.9959),
    "Raleigh-Cary, NC": ("Raleigh", 35.7796, -78.6382),
    "Miami-Fort Lauderdale-West Palm Beach, FL": ("Miami", 25.7617, -80.1918),
}

# Top 15 metros to label on the map. The rest get plotted as dots only (clean look).
LABELED_METROS = {
    "New York-Newark-Jersey City, NY-NJ",
    "Washington-Arlington-Alexandria, DC-VA-MD-WV",
    "San Francisco-Oakland-Fremont, CA",
    "San Jose-Sunnyvale-Santa Clara, CA",
    "Los Angeles-Long Beach-Anaheim, CA",
    "Boston-Cambridge-Newton, MA-NH",
    "Dallas-Fort Worth-Arlington, TX",
    "Seattle-Tacoma-Bellevue, WA",
    "Chicago-Naperville-Elgin, IL-IN",
    "Atlanta-Sandy Springs-Roswell, GA",
    "Austin-Round Rock-San Marcos, TX",
    "Denver-Aurora-Centennial, CO",
    "Pax River (Lexington Park), MD",  # below: handled via map
    "Lexington Park, MD",
    "Huntsville, AL",
    "Durham-Chapel Hill, NC",
    "Boulder, CO",
    "Pittsburgh, PA",
    "Miami-Fort Lauderdale-West Palm Beach, FL",
    "Houston-Pasadena-The Woodlands, TX",
}

# Per-label positioning override (some labels need bottom or right placement to avoid overlap)
LABEL_POSITION_OVERRIDE = {
    "San Jose": "bottom center",
    "San Francisco": "top left",
    "Pax River MD": "middle right",
    "Washington DC": "bottom center",
    "Boston": "top right",
    "Philadelphia": "bottom right",
    "Boulder": "top left",
    "Pittsburgh": "bottom center",
    "Huntsville": "bottom center",
    "Research Triangle": "middle right",
}


def main():
    df = pd.read_csv(DATA_DIR / "usa_ai_employment_by_msa.csv")
    print(f"Loaded {len(df)} rows")

    # Take top metros by absolute employment
    df_abs = df.sort_values("ai_emp", ascending=False).head(25).copy()
    # Plus top by concentration (some may overlap with absolute)
    df_conc = df.sort_values("ai_per_1000", ascending=False).head(15).copy()

    combined = pd.concat([df_abs, df_conc]).drop_duplicates(subset=["area"])
    combined = combined[combined["area"].isin(MSA_COORDS.keys())].copy()

    combined["city"] = combined["area"].map(lambda a: MSA_COORDS[a][0])
    combined["lat"] = combined["area"].map(lambda a: MSA_COORDS[a][1])
    combined["lon"] = combined["area"].map(lambda a: MSA_COORDS[a][2])

    # Only label top metros to avoid clutter; show all as dots
    combined["label"] = combined.apply(
        lambda r: r["city"] if r["area"] in LABELED_METROS else "", axis=1
    )

    # Per-label position overrides for clusters
    combined["textposition"] = combined["city"].map(
        lambda c: LABEL_POSITION_OVERRIDE.get(c, "top center")
    )

    # Hover text
    combined["hover"] = combined.apply(
        lambda r: f"<b>{r['city']}</b><br>{int(r['ai_emp']):,} AI workers<br>{r['ai_per_1000']:.1f} per 1,000 jobs",
        axis=1,
    )

    # Marker size based on absolute employment (sqrt scaling for visual balance)
    max_emp = combined["ai_emp"].max()
    combined["size"] = (combined["ai_emp"] / max_emp) ** 0.5 * 60 + 8

    # Color based on concentration (per_1000) — gold/orange for high concentration
    combined = combined.sort_values("ai_per_1000")

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=combined["lon"],
        lat=combined["lat"],
        text=combined["label"],
        textposition=combined["textposition"],
        mode="markers+text",
        marker=dict(
            size=combined["size"],
            color=combined["ai_per_1000"],
            colorscale=[[0, "#1e3a5f"], [0.3, "#3b6fa8"], [0.6, "#e89028"], [1.0, "#ffd400"]],
            cmin=1.5,
            cmax=8.0,
            showscale=True,
            colorbar=dict(
                title=dict(text="<b>AI workers<br>per 1,000 jobs</b>", font=dict(color="white", size=13)),
                tickfont=dict(color="white", size=11),
                bgcolor="rgba(0,0,0,0)",
                x=0.97,
            ),
            line=dict(color="white", width=1),
            opacity=0.92,
        ),
        textfont=dict(color="white", size=13, family="Helvetica, Arial, sans-serif"),
        hovertext=combined["hover"],
        hoverinfo="text",
        name="AI workers",
    ))

    fig.update_layout(
        geo=dict(
            scope="usa",
            projection=dict(type="albers usa"),
            showland=True,
            landcolor="#0a1628",
            countrycolor="#1a2942",
            subunitcolor="#1a2942",
            showlakes=False,
            bgcolor="#040810",
        ),
        paper_bgcolor="#040810",
        plot_bgcolor="#040810",
        title=dict(
            text="<b>WHERE AI WORKS IN AMERICA</b><br><span style='font-size:14px; color:#9eb3d6'>BLS Occupational Employment Statistics, May 2024 · SOC 15-1221 + 15-2051 · sized by absolute employment, colored by concentration</span>",
            font=dict(color="white", size=22, family="Helvetica, Arial, sans-serif"),
            x=0.05,
            xanchor="left",
            y=0.96,
        ),
        margin=dict(l=0, r=0, t=80, b=20),
        width=1920,
        height=1080,
        showlegend=False,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(OUTPUT_PATH), width=1920, height=1080, scale=1)
    print(f"\nSaved heatmap: {OUTPUT_PATH}")

    # Also write the analysis findings as a markdown summary
    findings_path = DATA_DIR / "usa_findings.md"
    df_top_abs = df.sort_values("ai_emp", ascending=False).head(15).reset_index(drop=True)
    df_top_conc = df.sort_values("ai_per_1000", ascending=False).head(15).reset_index(drop=True)

    lines = ["# USA AI Hub Findings — Original Analysis\n"]
    lines.append("**Data**: BLS OEWS, May 2024 release. SOC codes 15-1221 (Computer and Information Research Scientists) + 15-2051 (Data Scientists). Aggregated by Metropolitan Statistical Area.\n")
    lines.append("\n## Top 15 metros by absolute AI employment\n")
    lines.append("| # | Metro | AI workers | AI per 1,000 jobs |\n|---|---|---|---|\n")
    for i, r in df_top_abs.iterrows():
        lines.append(f"| {i+1} | {r['area']} | {int(r['ai_emp']):,} | {r['ai_per_1000']:.2f} |\n")
    lines.append("\n## Top 15 metros by AI concentration (per 1,000 workers)\n")
    lines.append("| # | Metro | AI per 1,000 | AI workers |\n|---|---|---|---|\n")
    for i, r in df_top_conc.iterrows():
        lines.append(f"| {i+1} | {r['area']} | {r['ai_per_1000']:.2f} | {int(r['ai_emp']):,} |\n")

    findings_path.write_text("".join(lines), encoding="utf-8")
    print(f"Saved findings: {findings_path}")


if __name__ == "__main__":
    main()

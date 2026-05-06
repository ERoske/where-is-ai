"""
Render the global AI research heatmap from OpenAlex data.

Filters out single-institution outliers (concept-mapping noise from fusion/biology
labs catching the broad "Artificial Intelligence" concept).
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "images" / "Heatmap-World-AI-Cities.png"

# Cities to relabel for clarity (OpenAlex sometimes returns ambiguous city names)
CITY_RELABEL = {
    ("Cambridge", "US"): "Boston/MIT",
    ("Mountain View", "US"): "Mountain View",
    ("Stanford", "US"): "Stanford",
    ("Pittsburgh", "US"): "Pittsburgh",
    ("Hong Kong", "HK"): "Hong Kong",
    ("Chennai", "IN"): "Chennai",
    ("Beijing", "CN"): "Beijing",
}

# Cities to actually LABEL on the map. Other cities show as dots only.
# Picked for narrative significance (size + surprise + geographic diversity).
LABEL_CITIES = {
    ("Beijing", "CN"),
    ("Shanghai", "CN"),
    ("Hangzhou", "CN"),
    ("Shenzhen", "CN"),
    ("Hong Kong", "HK"),
    ("Paris", "FR"),
    ("London", "GB"),
    ("Munich", "DE"),
    ("Zurich", "CH"),
    ("Singapore", "SG"),
    ("Seoul", "KR"),
    ("Toronto", "CA"),
    ("Sydney", "AU"),
    ("Melbourne", "AU"),
    ("Cambridge", "US"),
    ("Stanford", "US"),
    ("Mountain View", "US"),
    ("Pittsburgh", "US"),
    ("New York", "US"),
    ("Chennai", "IN"),
}

# Per-city label position override
LABEL_POSITION = {
    ("Beijing", "CN"): "top right",
    ("Shanghai", "CN"): "bottom right",
    ("Hangzhou", "CN"): "middle right",
    ("Shenzhen", "CN"): "bottom right",
    ("Hong Kong", "HK"): "bottom center",
    ("Stanford", "US"): "bottom left",
    ("Mountain View", "US"): "top left",
    ("Cambridge", "US"): "top right",
    ("Pittsburgh", "US"): "bottom center",
    ("New York", "US"): "bottom right",
    ("Chennai", "IN"): "bottom center",
    ("Singapore", "SG"): "bottom center",
    ("Melbourne", "AU"): "bottom center",
    ("Munich", "DE"): "bottom right",
    ("Zurich", "CH"): "top center",
}

# Manual whitelist for known AI hubs that may have only 1 institution in top 200 but matter
AI_HUB_WHITELIST = {
    ("Stanford", "US"),
    ("Berkeley", "US"),
    ("Pittsburgh", "US"),
    ("Tel Aviv-Yafo", "IL"),
    ("Lausanne", "CH"),
    ("Zürich", "CH"),
}


def main():
    df = pd.read_csv(DATA_DIR / "world_ai_research_by_city.csv")
    print(f"Loaded {len(df)} cities")

    # Filter: drop concept-mapping noise (single-institution outliers from non-AI fields).
    # Keep cities with 2+ institutions OR a single institution whose count is >= 1500
    # (which excludes the obvious noise like fusion-science labs while keeping real AI hubs
    # like Stanford, CMU, Mountain View/Google).
    keep_mask = (df["institutions"] >= 2) | (df["ai_works"] >= 1500)
    # Drop a small set of obvious concept-mapping artifacts
    NOISE_CITIES = {("Toki", "JP"), ("Braunschweig", "DE"), ("Nagoya", "JP")}
    keep_mask &= ~df.apply(lambda r: (r["city"], r["country_code"]) in NOISE_CITIES, axis=1)
    df = df[keep_mask].copy()
    print(f"After filter: {len(df)} cities")

    # Take top 30 by AI works
    df = df.sort_values("ai_works", ascending=False).head(30).reset_index(drop=True)

    # Relabel where helpful
    df["display"] = df.apply(
        lambda r: CITY_RELABEL.get((r["city"], r["country_code"]), r["city"]), axis=1
    )

    # Only show labels for selected cities
    df["label"] = df.apply(
        lambda r: r["display"] if (r["city"], r["country_code"]) in LABEL_CITIES else "", axis=1
    )

    # Per-city text position override (defaults to "top center")
    df["textposition"] = df.apply(
        lambda r: LABEL_POSITION.get((r["city"], r["country_code"]), "top center"), axis=1
    )

    # Sizing: sqrt scaling
    max_w = df["ai_works"].max()
    df["size"] = (df["ai_works"] / max_w) ** 0.55 * 60 + 10

    # Hover
    df["hover"] = df.apply(
        lambda r: f"<b>{r['display']}, {r['country']}</b><br>{int(r['ai_works']):,} AI/ML papers (last 12 months)<br>{int(r['institutions'])} top-200 institutions<br>Top: {r['top_institution']}",
        axis=1,
    )

    print("\nFinal top 25 cities for visualization:")
    print(df[["display", "country_code", "ai_works", "institutions", "lat", "lon"]].to_string(index=False))

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=df["lon"],
        lat=df["lat"],
        text=df["label"],
        textposition=df["textposition"],
        mode="markers+text",
        marker=dict(
            size=df["size"],
            color=df["ai_works"],
            colorscale=[[0, "#1e3a5f"], [0.25, "#3b6fa8"], [0.55, "#e89028"], [0.85, "#ffd400"], [1.0, "#ffefb3"]],
            cmin=df["ai_works"].min(),
            cmax=df["ai_works"].max() * 0.7,  # saturate the top so smaller cities still show
            showscale=True,
            colorbar=dict(
                title=dict(text="<b>AI papers<br>(12 mo)</b>", font=dict(color="white", size=13)),
                tickfont=dict(color="white", size=11),
                bgcolor="rgba(0,0,0,0)",
                x=0.97,
            ),
            line=dict(color="white", width=1.2),
            opacity=0.94,
        ),
        textfont=dict(color="white", size=14, family="Helvetica, Arial, sans-serif"),
        hovertext=df["hover"],
        hoverinfo="text",
        name="AI research output",
    ))

    fig.update_layout(
        geo=dict(
            projection=dict(type="natural earth"),
            showland=True,
            landcolor="#0a1628",
            countrycolor="#1a2942",
            subunitcolor="#1a2942",
            showlakes=False,
            showocean=True,
            oceancolor="#040810",
            coastlinecolor="#1f3554",
            bgcolor="#040810",
        ),
        paper_bgcolor="#040810",
        plot_bgcolor="#040810",
        title=dict(
            text="<b>WHERE AI RESEARCH HAPPENS</b><br><span style='font-size:14px; color:#9eb3d6'>OpenAlex · AI/ML papers published May 2025 to May 2026 · Top 200 institutions, aggregated by city · cities with 2+ contributing institutions</span>",
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

    # Save findings markdown
    findings = DATA_DIR / "world_findings.md"
    lines = ["# Global AI Research Hub Findings — Original Analysis\n"]
    lines.append("**Data**: OpenAlex API. AI/ML papers published 2025-05-06 through 2026-05-06. Top 200 institutions worldwide aggregated by city. Filter: cities with 2+ contributing institutions in the top 200.\n\n")
    lines.append("## Top 25 cities by AI/ML research output\n")
    lines.append("| # | City | Country | AI papers (12mo) | Institutions | Top institution |\n|---|---|---|---|---|---|\n")
    for i, r in df.iterrows():
        lines.append(f"| {i+1} | {r['display']} | {r['country']} | {int(r['ai_works']):,} | {int(r['institutions'])} | {r['top_institution']} |\n")
    findings.write_text("".join(lines), encoding="utf-8")
    print(f"Saved findings: {findings}")


if __name__ == "__main__":
    main()

"""
Render the global AI research heatmap from OpenAlex data, METRO-aggregated.

Reads world_ai_research_by_metro.csv (produced by aggregate_to_metro.py) which
groups fragmented U.S. cities into proper Census MSAs/CSAs (Bay Area, Boston Metro)
and combines Hong Kong's districts. International cities pass through unchanged
since they're already metro-coherent in OpenAlex's tagging.

Filters out single-institution concept-mapping noise (fusion/biology labs caught
in the broad "Artificial Intelligence" tag).
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "images" / "Heatmap-World-AI-Cities.png"

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
    ("Boston Metro", "US"),
    ("SF-San Jose Bay Area", "US"),
    ("Pittsburgh", "US"),
    ("New York", "US"),
    ("Chennai", "IN"),
    ("Bengaluru", "IN"),
}

# Per-metro label position override
LABEL_POSITION = {
    ("Beijing", "CN"): "top right",
    ("Shanghai", "CN"): "bottom right",
    ("Hangzhou", "CN"): "middle right",
    ("Shenzhen", "CN"): "bottom right",
    ("Hong Kong", "HK"): "bottom center",
    ("SF-San Jose Bay Area", "US"): "middle left",
    ("Boston Metro", "US"): "top right",
    ("Pittsburgh", "US"): "bottom center",
    ("New York", "US"): "bottom right",
    ("Chennai", "IN"): "bottom center",
    ("Singapore", "SG"): "bottom center",
    ("Melbourne", "AU"): "bottom center",
    ("Munich", "DE"): "bottom right",
    ("Zurich", "CH"): "top center",
}

# Manual whitelist for metros that may not pass the institution-count filter but matter
AI_HUB_WHITELIST = {
    ("Pittsburgh", "US"),
    ("Tel Aviv-Yafo", "IL"),
    ("Lausanne", "CH"),
    ("Zürich", "CH"),
}


def main():
    df = pd.read_csv(DATA_DIR / "world_ai_research_by_metro.csv")
    print(f"Loaded {len(df)} metros")

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

    # Display name = the metro name as-is
    df["display"] = df["city"]

    # Only show labels for selected metros
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
        title=dict(
            text="<b>WHERE AI RESEARCH HAPPENS</b><br><span style='font-size:14px; color:#9eb3d6'>OpenAlex · AI/ML papers May 2025 to May 2026 · Top 200 institutions, aggregated to METRO level</span>",
            font=dict(color="white", size=22, family="Helvetica, Arial, sans-serif"),
            x=0.05,
            xanchor="left",
            y=0.96,
        ),
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
    lines = ["# Global AI Research Hub Findings — Original Analysis (METRO level)\n"]
    lines.append("**Data**: OpenAlex API. AI/ML papers published 2025-05-06 through 2026-05-06. Top 200 institutions worldwide, aggregated to METRO level via hand-curated city→metro mapping (U.S. Census MSAs/CSAs for U.S. metros, OpenAlex city tags for everywhere else, Hong Kong districts consolidated).\n\n")
    lines.append("## Top 25 metros by AI/ML research output\n")
    lines.append("| # | Metro | Country | AI papers (12mo) | Institutions | Top institution |\n|---|---|---|---|---|---|\n")
    for i, r in df.iterrows():
        lines.append(f"| {i+1} | {r['display']} | {r['country']} | {int(r['ai_works']):,} | {int(r['institutions'])} | {r['top_institution']} |\n")
    findings.write_text("".join(lines), encoding="utf-8")
    print(f"Saved findings: {findings}")


if __name__ == "__main__":
    main()

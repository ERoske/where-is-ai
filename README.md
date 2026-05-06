# Where Is AI Actually Happening? An Open Data Analysis

By [Edward Roske](https://roske.ai). Methodology, raw data, and reproducible code behind the maps.

I kept reading "where the AI jobs are" articles that cited the same five rankings, all of which cited the same three reports, all of which cited each other. The data should be the news, not the citation chain. So I pulled the raw data myself.

This repo contains everything: the scripts, the data, the heatmaps, the findings.

## What's in here

- **`scripts/`** — Python code to fetch, analyze, and visualize. Six scripts, runnable on a fresh machine in under five minutes once dependencies are installed.
- **`data/`** — Raw CSVs from BLS and OpenAlex, plus aggregated findings.
- **`images/`** — The heatmaps and vertical social-post assets.

## The two questions

### 1. Where are the AI jobs in the USA?

Source: U.S. Bureau of Labor Statistics, **Occupational Employment and Wage Statistics (OEWS)**, May 2024 release (the most recent BLS has published as of May 2026; May 2025 typically drops in April-May 2026 and the fetch script is set up to use whichever release is current). Two AI-relevant SOC codes:

- **15-1221** — Computer and Information Research Scientists
- **15-2051** — Data Scientists

Aggregated by **Metropolitan Statistical Area (MSA)** — the U.S. Census/OMB definition that bundles a core city with its commuter-tied surrounding counties. So "San Francisco-Oakland-Fremont, CA" is the MSA, not just the city of San Francisco.

**Top finding by absolute employment**: New York leads at 21,240 AI workers, then DC (11,680), San Francisco-Oakland (11,210). The Bay Area splits across two BLS MSAs (SF-Oakland-Fremont + San Jose-Sunnyvale-Santa Clara) and rivals New York when summed.

**Top finding by concentration (per 1,000 jobs)**: San Jose dominates at 7.72/1,000. The genuine surprise is Lexington Park, Maryland at 6.98/1,000 — Naval Air Station Patuxent River drives it. Huntsville, Alabama (Redstone Arsenal) and Durham, NC (Research Triangle) round out the top concentration tier. Defense and research-anchored AI clusters are real and underreported.

Run it:

```bash
pip install -r requirements.txt
python scripts/fetch_bls_oews.py
python scripts/render_usa_heatmap.py
```

### 2. What are the biggest AI cities (metros) in the world?

Source: **OpenAlex** API. Papers tagged with the Artificial Intelligence concept (C154945302), published from 2025-05-06 to 2026-05-06. Top 200 institutions globally, geo-joined to city, then **metro-aggregated** via a hand-curated city→metro mapping (`scripts/aggregate_to_metro.py`).

**Why metro-aggregation matters**: OpenAlex tags institutions by city. Beijing's 15 universities all tag "Beijing" (one city = one metro = coherent). But the U.S. Bay Area gets fragmented across "Stanford," "Mountain View," "Berkeley," "San Francisco," and "San Jose" — five separate city tags for one metro. Without aggregation, the Bay Area looks small and China looks artificially dominant. The fix: roll fragmented U.S. cities into proper U.S. Census MSAs/CSAs, consolidate Hong Kong's districts, leave already-coherent international cities as-is.

**Could go more rigorous later** by joining against the EU JRC's [GHSL Urban Centre Database](https://ghsl.jrc.ec.europa.eu/) (~13,000 global urban centres). For now, the manual mapping covers the ~3 cases that actually fragment in our top-30 (Bay Area, Boston Metro, Hong Kong).

**Top finding**: Beijing leads at 42,843 AI papers in 12 months from 15 institutions — more than Paris, London, Munich, and Zurich combined. By metro count, **China takes 13 of the top 30**. Hong Kong (post-aggregation) jumps to #4 globally.

**The U.S. picture, properly aggregated**: SF-San Jose Bay Area lands at 6,997 papers from 3 top-200 institutions (Stanford + Google Mountain View + Berkeley). Boston Metro at 5,863 (Harvard + MIT + RES). Both are competitive globally but get dwarfed by Beijing, which is the actual story.

**Hidden hubs**: Switzerland's Zurich (ETH + EPFL) at 2,931 papers has the highest density per researcher on Earth. Singapore (NTU + NUS) at 5,725 is the densest non-Western AI economy. Hangzhou (DeepSeek + Six Little Dragons) at 10,550 is the underrecognized Chinese cluster.

Run it:

```bash
python scripts/fetch_openalex_world.py
python scripts/aggregate_to_metro.py    # NEW: city → metro aggregation
python scripts/render_world_heatmap.py
```

## Methodology and caveats

I'm measuring **different things** in each map. The U.S. map measures employment. The world map measures research output. They are not the same metric and combining them into a single ranking would be apples to oranges. Two slices of reality.

Other limitations to know:

- **AI definition is fuzzy.** SOC 15-1221 and 15-2051 are imperfect proxies for "AI workers." OpenAlex's "Artificial Intelligence" concept catches papers from biology, fusion physics, and other adjacent fields. I filtered the most obvious noise (single-institution outliers in non-AI fields like Toki and Braunschweig) but the concept boundary is genuinely soft.
- **Paper count is not paper quality.** NeurIPS and ICML acceptances still skew heavily American. Chinese AI research clusters in mid-tier journals more than Western research does. Volume and quality are different metrics.
- **Metro aggregation is hand-curated, not algorithmic.** I rolled fragmented U.S. cities (Bay Area, Boston Metro) into proper Census MSAs/CSAs and consolidated Hong Kong's districts. The mapping is in `scripts/aggregate_to_metro.py` and covers the ~3 cases that actually fragment in our top 30. International cities pass through unchanged because OpenAlex's tagging is already metro-coherent (Beijing's 15 institutions all tag "Beijing"). For more rigorous future global aggregation, the upgrade path is the EU JRC's GHSL Urban Centre Database.
- **Snapshot, not trend.** This is one moment in time. The cities that climb in the next five years will be the ones combining cheap living, world-class universities, and government willingness to write big checks. I'll re-run this quarterly.

If you find a number wrong, the data and code are here. I would rather correct a number than defend one.

## Reproducibility

Python 3.11+. Dependencies in `requirements.txt`. Run scripts in order:

```bash
pip install -r requirements.txt

# USA (BLS)
python scripts/fetch_bls_oews.py
python scripts/render_usa_heatmap.py

# World (OpenAlex) — metro-aggregated
python scripts/fetch_openalex_world.py
python scripts/aggregate_to_metro.py
python scripts/render_world_heatmap.py

# Optional: vertical social posts
python scripts/compose_vertical_shorts.py
python scripts/compose_top10_verticals.py
```

The first BLS run downloads a 38 MB zip from bls.gov and caches it locally. OpenAlex queries are ungated but rate-limited; the world fetch takes a few minutes.

## License

MIT for code. Data files are in the public domain (BLS) or available under OpenAlex's CC0 license.

## Get in touch

Asking good questions: [edward@roske.ai](mailto:edward@roske.ai)
"Asking Good Questions" podcast and YouTube videos: [roske.ai](https://roske.ai)

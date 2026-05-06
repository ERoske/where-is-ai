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

Source: U.S. Bureau of Labor Statistics, **Occupational Employment and Wage Statistics (OEWS)**, May 2024 release. Two AI-relevant SOC codes:

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

### 2. What are the biggest AI cities in the world?

Source: **OpenAlex** API. Papers tagged with the Artificial Intelligence concept (C154945302), published from 2025-05-06 to 2026-05-06. Top 200 institutions globally, geo-joined to city.

Aggregation note: the world data uses **city** (from OpenAlex's institution metadata), not MSA. This means Stanford, Mountain View, Berkeley, and San Francisco show up as separate cities even though they're the same metro. **This makes China look more dominant than it would on a metro-to-metro basis** — Beijing's 15 institutions all tag "Beijing," while the U.S. Bay Area gets fragmented across half a dozen city names. I treat this as a known limitation in the writeup, not a finding.

**Top finding**: Beijing leads at 42,843 AI papers in 12 months from 15 institutions — more than Paris, London, Munich, and Zurich combined. By city count, China takes 14 of the top 30. The U.S. is competitive but distributed.

**Hidden hubs**: Switzerland's Zurich (ETH + EPFL) at 2,931 papers from two institutions has the highest density per researcher on Earth. Singapore (NTU + NUS) at 5,725 papers is the densest non-Western AI economy. Hangzhou (Six Little Dragons + DeepSeek) at 10,550 from five institutions is the underrecognized Chinese cluster.

Run it:

```bash
python scripts/fetch_openalex_world.py
python scripts/render_world_heatmap.py
```

## Methodology and caveats

I'm measuring **different things** in each map. The U.S. map measures employment. The world map measures research output. They are not the same metric and combining them into a single ranking would be apples to oranges. Two slices of reality.

Other limitations to know:

- **AI definition is fuzzy.** SOC 15-1221 and 15-2051 are imperfect proxies for "AI workers." OpenAlex's "Artificial Intelligence" concept catches papers from biology, fusion physics, and other adjacent fields. I filtered the most obvious noise (single-institution outliers in non-AI fields like Toki and Braunschweig) but the concept boundary is genuinely soft.
- **Paper count is not paper quality.** NeurIPS and ICML acceptances still skew heavily American. Chinese AI research clusters in mid-tier journals more than Western research does. Volume and quality are different metrics.
- **The world data fragments U.S. metros.** See the note above. If anything, the China dominance is overstated by roughly the size of the Bay Area aggregation gap.
- **Snapshot, not trend.** This is one moment in time. The cities that climb in the next five years will be the ones combining cheap living, world-class universities, and government willingness to write big checks. I'll re-run this quarterly.

If you find a number wrong, the data and code are here. I would rather correct a number than defend one.

## Reproducibility

Python 3.11+. Dependencies in `requirements.txt`. Run scripts in order:

```bash
pip install -r requirements.txt

# USA (BLS)
python scripts/fetch_bls_oews.py
python scripts/render_usa_heatmap.py

# World (OpenAlex)
python scripts/fetch_openalex_world.py
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

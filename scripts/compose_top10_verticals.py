"""
Compose 1080x1920 vertical "Top 10" list cards for carousel-style social posts.

USA: Top 10 metros by absolute AI employment (BLS).
World: Top 10 cities by AI/ML paper output (OpenAlex).
"""
from pathlib import Path
import pandas as pd

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "images"

CANVAS_W = 1080
CANVAS_H = 1920

BG = (4, 8, 16)
ACCENT = (255, 212, 0)
TEXT = (255, 255, 255)
SUB = (158, 179, 214)
ROW_BG_ALT = (12, 22, 40)


def find_font(size, bold=False):
    candidates_bold = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]
    candidates_regular = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    for path in (candidates_bold if bold else candidates_regular):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# Display name overrides for readability
USA_LABEL_MAP = {
    "New York-Newark-Jersey City, NY-NJ": "New York",
    "Washington-Arlington-Alexandria, DC-VA-MD-WV": "Washington DC",
    "San Francisco-Oakland-Fremont, CA": "San Francisco",
    "Los Angeles-Long Beach-Anaheim, CA": "Los Angeles",
    "Boston-Cambridge-Newton, MA-NH": "Boston",
    "Dallas-Fort Worth-Arlington, TX": "Dallas",
    "San Jose-Sunnyvale-Santa Clara, CA": "San Jose",
    "Seattle-Tacoma-Bellevue, WA": "Seattle",
    "Chicago-Naperville-Elgin, IL-IN": "Chicago",
    "Atlanta-Sandy Springs-Roswell, GA": "Atlanta",
    "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": "Philadelphia",
    "Houston-Pasadena-The Woodlands, TX": "Houston",
    "Denver-Aurora-Centennial, CO": "Denver",
    "San Diego-Chula Vista-Carlsbad, CA": "San Diego",
    "Charlotte-Concord-Gastonia, NC-SC": "Charlotte",
    "Austin-Round Rock-San Marcos, TX": "Austin",
}

WORLD_LABEL_MAP = {
    ("Beijing", "CN"): ("Beijing", "China"),
    ("Shanghai", "CN"): ("Shanghai", "China"),
    ("Nanjing", "CN"): ("Nanjing", "China"),
    ("Hangzhou", "CN"): ("Hangzhou", "China"),
    ("Paris", "FR"): ("Paris", "France"),
    ("Chennai", "IN"): ("Chennai", "India"),
    ("Wuhan", "CN"): ("Wuhan", "China"),
    ("Xi'an", "CN"): ("Xi'an", "China"),
    ("Guangzhou", "CN"): ("Guangzhou", "China"),
    ("Hong Kong", "HK"): ("Hong Kong", "Hong Kong"),
    ("London", "GB"): ("London", "United Kingdom"),
    ("Chengdu", "CN"): ("Chengdu", "China"),
    ("SF-San Jose Bay Area", "US"): ("SF-Bay Area", "United States"),
    ("Boston Metro", "US"): ("Boston Metro", "United States"),
}


def draw_card(rows, title, subtitle, source, output_path, value_format="{:,}"):
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    # Top gold band
    draw.rectangle([(0, 0), (CANVAS_W, 12)], fill=ACCENT)

    # Brand
    brand_font = find_font(30, bold=True)
    bbox = draw.textbbox((0, 0), "ASKING GOOD QUESTIONS", font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - bw) / 2, 50), "ASKING GOOD QUESTIONS", fill=ACCENT, font=brand_font)

    # Title
    title_font = find_font(74, bold=True)
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - tw) / 2, 130), title, fill=TEXT, font=title_font)

    # Subtitle
    sub_font = find_font(28, bold=False)
    bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    sw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - sw) / 2, 230), subtitle, fill=SUB, font=sub_font)

    # Rows: 10 rows, each ~135px tall
    row_top = 310
    row_h = 135
    rank_font = find_font(60, bold=True)
    name_font = find_font(48, bold=True)
    detail_font = find_font(28, bold=False)
    value_font = find_font(54, bold=True)

    for i, (name, detail, value) in enumerate(rows):
        y = row_top + i * row_h
        # Alternating row background
        if i % 2 == 0:
            draw.rectangle([(40, y - 8), (CANVAS_W - 40, y + row_h - 18)], fill=ROW_BG_ALT)

        # Rank
        rank = f"{i+1:02d}"
        draw.text((70, y + 22), rank, fill=ACCENT, font=rank_font)

        # City name
        draw.text((220, y + 14), name, fill=TEXT, font=name_font)

        # Detail (country / state)
        if detail:
            draw.text((220, y + 76), detail, fill=SUB, font=detail_font)

        # Value (right aligned)
        value_str = value_format.format(value)
        bbox = draw.textbbox((0, 0), value_str, font=value_font)
        vw = bbox[2] - bbox[0]
        draw.text((CANVAS_W - 70 - vw, y + 28), value_str, fill=TEXT, font=value_font)

    # Source line
    src_font = find_font(24, bold=False)
    src_y = row_top + 10 * row_h + 30
    bbox = draw.textbbox((0, 0), source, font=src_font)
    sw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - sw) / 2, src_y), source, fill=SUB, font=src_font)

    # CTA
    cta_font = find_font(38, bold=True)
    cta = "Full analysis: roske.ai"
    bbox = draw.textbbox((0, 0), cta, font=cta_font)
    cw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - cw) / 2, CANVAS_H - 100), cta, fill=ACCENT, font=cta_font)

    # Bottom gold band
    draw.rectangle([(0, CANVAS_H - 12), (CANVAS_W, CANVAS_H)], fill=ACCENT)

    canvas.save(output_path, "PNG")
    print(f"Saved: {output_path}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # USA TOP 10 (by absolute AI employment)
    df_usa = pd.read_csv(DATA_DIR / "usa_ai_employment_by_msa.csv")
    df_usa = df_usa.sort_values("ai_emp", ascending=False).head(10)
    usa_rows = []
    for _, r in df_usa.iterrows():
        name = USA_LABEL_MAP.get(r["area"], r["area"].split(",")[0])
        # Pull state code from MSA string (e.g., "..., NY-NJ")
        state = r["area"].split(",")[-1].strip().split("-")[0] if "," in r["area"] else ""
        usa_rows.append((name, f"{state} metro" if state else "", int(r["ai_emp"])))
    draw_card(
        rows=usa_rows,
        title="TOP 10 U.S. AI CITIES",
        subtitle="Ranked by AI workforce employment",
        source="Source: BLS OEWS May 2025  ·  SOC 15-1221 + 15-2051  ·  My own analysis",
        output_path=OUT_DIR / "USA-Top-10-AI-Cities-Vertical.png",
        value_format="{:,}",
    )

    # WORLD TOP 10 (by AI paper output, METRO-aggregated)
    df_w = pd.read_csv(DATA_DIR / "world_ai_research_by_metro.csv")
    df_w = df_w.sort_values("ai_works", ascending=False)
    # Apply same filter as the heatmap render: 2+ institutions OR 1500+ works,
    # excluding noise cities
    NOISE = {("Toki", "JP"), ("Braunschweig", "DE"), ("Nagoya", "JP")}
    keep = df_w.apply(
        lambda r: ((r["institutions"] >= 2) or (r["ai_works"] >= 1500))
        and (r["city"], r["country_code"]) not in NOISE,
        axis=1,
    )
    df_w = df_w[keep].head(10)

    world_rows = []
    for _, r in df_w.iterrows():
        key = (r["city"], r["country_code"])
        display, country = WORLD_LABEL_MAP.get(key, (r["city"], r["country"]))
        world_rows.append((display, country, int(r["ai_works"])))

    draw_card(
        rows=world_rows,
        title="TOP 10 GLOBAL AI METROS",
        subtitle="Ranked by AI/ML papers, last 12 months (metro-aggregated)",
        source="Source: OpenAlex  ·  May 2025 to May 2026  ·  My own analysis",
        output_path=OUT_DIR / "World-Top-10-AI-Cities-Vertical.png",
        value_format="{:,}",
    )


if __name__ == "__main__":
    main()

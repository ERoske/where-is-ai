"""
Compose 1080x1920 vertical hero frames for Instagram Reels / YouTube Shorts.

Layout (per frame):
  - Top: bold question (the slide 1 hook)
  - Middle: heatmap (scaled to fit width)
  - Bottom: closing question + source line

Outputs two PNGs to outputs/Generated Images/ for Reels-ready vertical assets.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "images"

CANVAS_W = 1080
CANVAS_H = 1920

BG = (4, 8, 16)            # near-black navy
ACCENT = (255, 212, 0)     # gold
TEXT = (255, 255, 255)
SUB = (158, 179, 214)


def find_font(size, bold=False):
    """Find a usable system font on Windows. Falls back to default."""
    candidates_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]
    candidates_regular = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in (candidates_bold if bold else candidates_regular):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_text_block(draw, text, font, x, y, color, max_width, line_spacing=1.15):
    """Draw wrapped text starting at (x, y). Returns the y after drawing."""
    lines = wrap_text(draw, text, font, max_width)
    line_h = font.size * line_spacing
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text((x + (max_width - w) / 2, y), line, fill=color, font=font)
        y += line_h
    return int(y)


def compose(heatmap_path, title, closing_q, source, output_path):
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    # Brand band at top
    draw.rectangle([(0, 0), (CANVAS_W, 12)], fill=ACCENT)

    # Top: brand line
    brand_font = find_font(34, bold=True)
    bbox = draw.textbbox((0, 0), "ASKING GOOD QUESTIONS", font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - bw) / 2, 50), "ASKING GOOD QUESTIONS", fill=ACCENT, font=brand_font)

    # Title (the hook)
    title_font = find_font(72, bold=True)
    title_y = draw_text_block(draw, title, title_font, x=60, y=140, color=TEXT, max_width=CANVAS_W - 120, line_spacing=1.1)

    # Heatmap
    hm = Image.open(heatmap_path).convert("RGB")
    hm_w, hm_h = hm.size
    target_w = CANVAS_W - 80
    scale = target_w / hm_w
    target_h = int(hm_h * scale)
    hm_resized = hm.resize((target_w, target_h), Image.LANCZOS)
    hm_y = title_y + 40
    canvas.paste(hm_resized, (40, hm_y))
    hm_bottom = hm_y + target_h

    # Closing question (centered, white)
    close_font = find_font(54, bold=True)
    close_y = hm_bottom + 60
    close_y = draw_text_block(draw, closing_q, close_font, x=60, y=close_y, color=TEXT, max_width=CANVAS_W - 120, line_spacing=1.15)

    # Source line
    src_font = find_font(28, bold=False)
    src_y = close_y + 30
    bbox = draw.textbbox((0, 0), source, font=src_font)
    sw = bbox[2] - bbox[0]
    draw.text(((CANVAS_W - sw) / 2, src_y), source, fill=SUB, font=src_font)

    # CTA at bottom
    cta_font = find_font(40, bold=True)
    cta = "Full breakdown in the video"
    bbox = draw.textbbox((0, 0), cta, font=cta_font)
    cw = bbox[2] - bbox[0]
    cta_y = CANVAS_H - 130
    draw.text(((CANVAS_W - cw) / 2, cta_y), cta, fill=ACCENT, font=cta_font)

    # Bottom band
    draw.rectangle([(0, CANVAS_H - 12), (CANVAS_W, CANVAS_H)], fill=ACCENT)

    canvas.save(output_path, "PNG")
    print(f"Saved: {output_path}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # USA vertical
    compose(
        heatmap_path=OUT_DIR / "Heatmap-USA-AI-Jobs.png",
        title="Where are the AI jobs in the USA?",
        closing_q="Did your city make the map?",
        source="Source: BLS OEWS May 2024 (SOC 15-1221 + 15-2051)  ·  My own analysis",
        output_path=OUT_DIR / "Heatmap-USA-AI-Jobs-Vertical.png",
    )

    # World vertical
    compose(
        heatmap_path=OUT_DIR / "Heatmap-World-AI-Cities.png",
        title="What are the biggest AI cities in the world?",
        closing_q="Where would you bet a billion dollars?",
        source="Source: OpenAlex API  ·  AI papers, last 12 months  ·  My own analysis",
        output_path=OUT_DIR / "Heatmap-World-AI-Cities-Vertical.png",
    )


if __name__ == "__main__":
    main()

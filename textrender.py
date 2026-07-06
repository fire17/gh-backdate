"""
textrender.py — rasterize text into a COLS x ROWS binary grid (1 = "lit" pixel).

Strategy (auto-fit, aspect-preserving):
  1. Render the text large in a real TTF (roman serif or narrow sans).
  2. Tight-crop to the ink bounding box  -> a high-res "master" glyph strip.
  3. Scale the master DOWN to fit inside (avail_cols x rows), preserving aspect
     ratio, so the phrase width ALWAYS fits the matrix — height fills up to 7px,
     width never exceeds the addressable columns.
  4. Threshold to binary and center the result in the full COLS x ROWS grid.

This is why "text width adapts to always fit the matrix": whichever dimension
binds (width for long phrases, height for short ones) is the one clamped.
"""

from __future__ import annotations
from PIL import Image, ImageDraw, ImageFont

# Curated font choices. .ttc files need a face index.
FONTS = {
    "times":        ("/System/Library/Fonts/Supplemental/Times New Roman.ttf", 0),
    "times_bold":   ("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", 0),
    "bodoni":       ("/System/Library/Fonts/Supplemental/Bodoni 72.ttc", 0),
    "baskerville":  ("/System/Library/Fonts/Supplemental/Baskerville.ttc", 0),
    "georgia":      ("/System/Library/Fonts/Supplemental/Georgia.ttf", 0),
    "didot":        ("/System/Library/Fonts/Supplemental/Didot.ttc", 0),
    "arial_narrow": ("/System/Library/Fonts/Supplemental/Arial Narrow.ttf", 0),
    "arial_narrow_bold": ("/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf", 0),
    "din_condensed": ("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf", 0),
}


def _load(font_key: str, size: int) -> ImageFont.FreeTypeFont:
    path, idx = FONTS[font_key]
    return ImageFont.truetype(path, size, index=idx)


def render_master(text: str, font_key: str, px_height: int = 400,
                  tracking: float = 0.0) -> Image.Image:
    """Render `text` big, return the tight-cropped grayscale ink strip."""
    font = _load(font_key, px_height)
    # generous canvas
    canvas = Image.new("L", (px_height * (len(text) + 2), px_height * 3), 0)
    d = ImageDraw.Draw(canvas)
    if tracking:
        # manual letter spacing
        x = px_height
        y = px_height
        for ch in text:
            d.text((x, y), ch, fill=255, font=font)
            bb = font.getbbox(ch)
            adv = (bb[2] - bb[0]) if ch != " " else px_height * 0.3
            x += adv + tracking * px_height
    else:
        d.text((px_height, px_height), text, fill=255, font=font)
    bbox = canvas.getbbox()
    return canvas.crop(bbox) if bbox else canvas


def text_to_grid(text: str, cols: int, rows: int, font_key: str = "times_bold",
                 pad_lr: int = 0, threshold_ratio: float = 0.42,
                 tracking: float = 0.0) -> list[list[int]]:
    """Return a rows x cols binary grid (list of rows of 0/1)."""
    avail_w = cols - 2 * pad_lr
    master = render_master(text, font_key, tracking=tracking)
    mw, mh = master.size

    # aspect-preserving fit into avail_w x rows
    scale = min(avail_w / mw, rows / mh)
    tw = max(1, min(avail_w, round(mw * scale)))
    th = max(1, min(rows, round(mh * scale)))
    small = master.resize((tw, th), Image.LANCZOS)

    # threshold relative to this image's peak brightness (robust at tiny sizes)
    peak = max(1, small.getextrema()[1])
    thr = peak * threshold_ratio
    px = small.load()

    # center within full grid
    x0 = (cols - tw) // 2
    y0 = (rows - th) // 2
    grid = [[0] * cols for _ in range(rows)]
    for y in range(th):
        for x in range(tw):
            if px[x, y] >= thr:
                grid[y0 + y][x0 + x] = 1
    return grid


def grid_ascii(grid: list[list[int]], on: str = "██", off: str = "··") -> str:
    return "\n".join("".join(on if c else off for c in row) for row in grid)


def grid_stats(grid: list[list[int]]) -> tuple[int, int]:
    lit = sum(sum(r) for r in grid)
    return lit, len(grid) * len(grid[0])

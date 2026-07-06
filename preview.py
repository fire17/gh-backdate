"""
preview.py — render a COLS x ROWS binary grid as a GitHub-style contributions PNG.

Upscales each cell to a rounded square on the GitHub dark background so the
banner can be eyeballed exactly as it will appear on the profile.
"""

from __future__ import annotations
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from gridmap import Grid
from shade import SHADES

# GitHub dark-theme palette
BG = (13, 17, 23)          # #0d1117 page
EMPTY = SHADES[0]          # #161b22 empty cell
TEXT = (139, 148, 158)     # #8b949e muted labels

CELL = 22                  # px per cell
GAP = 4                    # px between cells
PAD = 34                   # outer padding
RADIUS = 5


def _label_font(size: int):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_png(grid: list[list[int]], out_path: str, ref_day: date | None = None,
               title: str | None = None):
    rows = len(grid)
    cols = len(grid[0])
    step = CELL + GAP
    top_labels = 20
    left_labels = 30
    grid_w = cols * step - GAP
    grid_h = rows * step - GAP
    W = PAD * 2 + left_labels + grid_w
    H = PAD * 2 + top_labels + grid_h + (28 if title else 0)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    ox = PAD + left_labels
    oy = PAD + top_labels

    g = Grid(ref_day) if ref_day else Grid(date.today())

    # month labels along the top (where a new month begins in that column)
    lf = _label_font(15)
    last_month = None
    for col in range(cols):
        mdate = g.date_at(col, 0)
        if mdate.month != last_month:
            last_month = mdate.month
            d.text((ox + col * step, PAD), mdate.strftime("%b"), fill=TEXT, font=lf)

    # weekday labels (Mon/Wed/Fri like GitHub)
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        d.text((PAD, oy + row * step + 3), name, fill=TEXT, font=lf)

    # cells (value 0..4 -> shade tier)
    for r in range(rows):
        for c in range(cols):
            x = ox + c * step
            y = oy + r * step
            color = SHADES.get(grid[r][c], EMPTY)
            d.rounded_rectangle([x, y, x + CELL, y + CELL], radius=RADIUS, fill=color)

    # Less [ ][ ][ ][ ][ ] More legend (bottom-right)
    lf2 = _label_font(14)
    lx = ox + grid_w - 5 * (CELL // 2 + 3) - 70
    ly = oy + grid_h + 8
    d.text((lx, ly), "Less", fill=TEXT, font=lf2)
    for i in range(5):
        cx = lx + 34 + i * (CELL // 2 + 3)
        d.rounded_rectangle([cx, ly, cx + CELL // 2, ly + CELL // 2],
                            radius=3, fill=SHADES[i])
    d.text((lx + 34 + 5 * (CELL // 2 + 3) + 4, ly), "More", fill=TEXT, font=lf2)

    if title:
        tf = _label_font(18)
        d.text((ox, H - PAD - 6), title, fill=TEXT, font=tf)

    img.save(out_path)
    return out_path

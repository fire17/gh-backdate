"""
build.py — render a phrase across candidate fonts, print ASCII + corners,
and stack all variants into one comparison PNG for eyeballing.

Usage: python3 build.py "Open Your Mind"
"""

from __future__ import annotations
import sys
from datetime import date
from PIL import Image
from gridmap import Grid, COLS, ROWS
from textrender import text_to_grid, grid_ascii, grid_stats
from preview import render_png

CANDIDATES = [
    ("times_bold",   0.42, 0.0),
    ("bodoni",       0.40, 0.0),
    ("baskerville",  0.42, 0.0),
    ("georgia",      0.42, 0.0),
    ("arial_narrow_bold", 0.45, 0.0),
    ("din_condensed", 0.45, 0.0),
]


def main():
    text = sys.argv[1] if len(sys.argv) > 1 else "Open Your Mind"
    outdir = "/Users/magic/Creations/Lively/gh-banner/out"
    import os
    os.makedirs(outdir, exist_ok=True)

    g = Grid(date.today())
    print(f"=== date grid ({g.cols}x{g.rows}), reference {g.today} "
          f"({g.today.strftime('%A')}) ===")
    for name, dd in g.corners().items():
        print(f"  {name:13s}: {dd} ({dd.strftime('%A')})")
    print(f'\n=== phrase: "{text}" ===\n')

    panels = []
    for key, thr, trk in CANDIDATES:
        grid = text_to_grid(text, COLS, ROWS, font_key=key,
                            threshold_ratio=thr, tracking=trk)
        lit, total = grid_stats(grid)
        print(f"--- {key}  (lit {lit}/{total}) ---")
        print(grid_ascii(grid))
        print()
        png = f"{outdir}/{key}.png"
        render_png(grid, png, ref_day=g.today, title=f'{key}  —  "{text}"')
        panels.append(png)

    # stack all variants vertically into one comparison sheet
    imgs = [Image.open(p) for p in panels]
    w = max(i.width for i in imgs)
    gap = 16
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    sheet = Image.new("RGB", (w, h), (13, 17, 23))
    y = 0
    for im in imgs:
        sheet.paste(im, (0, y))
        y += im.height + gap
    comp = f"{outdir}/COMPARISON.png"
    sheet.save(comp)
    print(f"comparison sheet: {comp}")
    print(f"individual PNGs : {outdir}/<font>.png")


if __name__ == "__main__":
    main()

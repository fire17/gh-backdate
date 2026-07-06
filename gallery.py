#!/usr/bin/env python3
"""gallery.py — render a matrix of font x style options and open one big sheet."""

from __future__ import annotations
import os
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from gridmap import Grid, COLS, ROWS
from fonts import render_mask
from styles import apply_style
from preview import render_png

TEXT = "Open Your Mind"

# (font, style, label)
COMBOS = [
    ("normal", "none", "normal · plain"),
    ("normal", "twotone", "normal · twotone"),
    ("normal", "twinkle", "normal · twinkle (Sun/Sat stars)"),
    ("normal", "drop", "normal · drop-shadow"),
    ("normal", "outline", "normal · outline"),
    ("opencode", "none", "OPENCODE · plain"),
    ("opencode", "native", "OPENCODE · native two-tone"),
    ("opencode", "twinkle", "OPENCODE · twinkle"),
    ("times", "none", "times roman · plain"),
    ("bodoni", "none", "bodoni · plain"),
    ("baskerville", "none", "baskerville · plain"),
    ("arial_narrow", "none", "arial narrow · plain"),
    ("din_condensed", "none", "din condensed · plain"),
]


def build():
    outdir = "/Users/magic/Creations/Lively/gh-banner/out"
    os.makedirs(outdir, exist_ok=True)
    g = Grid(date.today())
    panels = []
    for font, style, label in COMBOS:
        mask, zone, tw = render_mask(TEXT, COLS, ROWS, font=font)
        grid = apply_style(mask, mode=style, zone=zone, seed_text=TEXT)
        p = f"{outdir}/opt_{font}_{style}.png"
        render_png(grid, p, ref_day=g.today, title=label)
        panels.append(p)

    imgs = [Image.open(p) for p in panels]
    w = max(i.width for i in imgs)
    gap = 14
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    sheet = Image.new("RGB", (w, h), (13, 17, 23))
    y = 0
    for im in imgs:
        sheet.paste(im, (0, y))
        y += im.height + gap
    comp = f"{outdir}/OPTIONS.png"
    sheet.save(comp)
    print("wrote", comp, "with", len(panels), "options")
    return comp


if __name__ == "__main__":
    comp = build()
    os.system(f'open "{comp}"')

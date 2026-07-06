"""
fonts.py — unified multi-font text -> binary grid renderer.

Fonts:
  "normal"      : the hand-built 5-tall pixel font (default; most compact)
  "opencode"    : OpenCodeLogo 7x4 blocky pixel font (github pantheon-org)
  "times" / "bodoni" / "baskerville" / "arial_narrow" / "din_condensed"
                : real TTF rasterized + thresholded (roman/narrow looks)

All return a rows x cols grid of 0/1, width auto-fit to the matrix.
For "opencode", `native_zone_grid` also exposes its built-in PRIMARY(top)/
SECONDARY(bottom) two-tone so styles can honour it.
"""

from __future__ import annotations
from bitmapfont import render_word as _normal_word
from opencode_font import OC_GLYPHS, oc_width
from textrender import text_to_grid as _ttf_grid

BITMAP_FONTS = {"normal", "opencode"}
TTF_FONTS = {"times", "bodoni", "baskerville", "arial_narrow", "din_condensed"}
TTF_KEY = {"times": "times_bold", "arial_narrow": "arial_narrow_bold"}
ALL_FONTS = ["normal", "opencode", "times", "bodoni", "baskerville",
             "arial_narrow", "din_condensed"]


def _oc_layout_width(text, gap, word_gap):
    w = 0
    prev = False
    for ch in text:
        if ch == " ":
            w += word_gap
            prev = False
            continue
        gw = oc_width(ch)
        if gw == 0:
            continue
        if prev:
            w += gap
        w += gw
        prev = True
    return w


def _render_opencode(text, cols, rows):
    """Return (binary_grid, zone_grid). zone: 1=primary(top) 2=secondary(bottom)."""
    text = text.upper()
    gap, wg = 1, 2
    while _oc_layout_width(text, gap, wg) > cols and wg > 0:
        wg -= 1
    while _oc_layout_width(text, gap, wg) > cols and gap > 0:
        gap -= 1
    total = _oc_layout_width(text, gap, wg)
    grid = [[0] * cols for _ in range(rows)]
    zone = [[0] * cols for _ in range(rows)]
    x0 = max(0, (cols - total) // 2)
    x = x0
    prev = False
    for ch in text:
        if ch == " ":
            x += wg
            prev = False
            continue
        g = OC_GLYPHS.get(ch)
        if g is None:
            continue
        if prev:
            x += gap
        gw = oc_width(ch)
        for ry in range(7):
            row = g[ry]
            for rx, v in enumerate(row):
                if v and 0 <= x + rx < cols and ry < rows:
                    grid[ry][x + rx] = 1
                    # OpenCode auto rule: rows 1-2 primary, 3-5 secondary
                    zone[ry][x + rx] = 1 if ry <= 2 else 2
        x += gw
        prev = True
    return grid, zone, total, gap, wg


def render_mask(text, cols, rows, font="normal"):
    """Return a rows x cols binary grid for `text` in `font`."""
    if font == "normal":
        grid, tw, g, wg = _normal_word(text, cols, rows)
        return grid, None, tw
    if font == "opencode":
        grid, zone, tw, g, wg = _render_opencode(text, cols, rows)
        return grid, zone, tw
    if font in TTF_FONTS:
        key = TTF_KEY.get(font, font)
        grid = _ttf_grid(text, cols, rows, font_key=key, threshold_ratio=0.42)
        tw = max((sum(r) and max(i for i, v in enumerate(r) if v) for r in grid),
                 default=0)
        return grid, None, cols
    raise ValueError(f"unknown font {font!r}")

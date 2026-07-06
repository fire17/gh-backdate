#!/usr/bin/env python3
"""
animate.py — slide a 53-week window across the long tape and save a GIF.

Each frame advances the window by ONE column (= one week). Content scrolls left
like a marquee; the caption shows the real date/year of the rightmost (current)
week, so you watch the years tick by.

Plain by default (single bright shade, no shadows/gradients).
"""

from __future__ import annotations
import argparse
import os
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont

from gridmap import Grid, COLS, ROWS
from shade import SHADES
from strip import build_strip, SCRIPT

CELL, GAP, PAD = 12, 3, 16
LEFT_LBL, TOP, CAPTION = 30, 4, 26
BG = (13, 17, 23)
TEXT = (139, 148, 158)
ACCENT = (57, 211, 83)


def _font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def render_frame(window, right_date: date, week_idx: int, years_total: int):
    step = CELL + GAP
    gw = COLS * step - GAP
    gh = ROWS * step - GAP
    W = PAD * 2 + LEFT_LBL + gw
    H = PAD * 2 + TOP + gh + CAPTION
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    ox = PAD + LEFT_LBL
    oy = PAD + TOP
    lf = _font(13)
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        d.text((PAD, oy + row * step + 1), name, fill=TEXT, font=lf)
    for r in range(ROWS):
        for c in range(COLS):
            v = window[r][c]
            color = SHADES[4] if v else SHADES[0]
            x = ox + c * step
            y = oy + r * step
            d.rounded_rectangle([x, y, x + CELL, y + CELL], radius=3, fill=color)
    cf = _font(15)
    yr = (right_date.year)
    d.text((ox, oy + gh + 7),
           f"week {week_idx:>3}   ·   {right_date:%b %Y}   ·   {right_date:%Y-%m-%d}",
           fill=TEXT, font=cf)
    d.text((W - PAD - 90, oy + gh + 7), f"{years_total}-yr scroll", fill=ACCENT, font=cf)
    return img


def build_gif(years: int = 10, out: str = None, step_weeks: int = 1,
              hold_start: int = 10, ms: int = 55):
    out = out or "/Users/magic/Creations/Lively/gh-banner/out/scroll.gif"
    g = Grid(date.today())
    base_left_sunday = g.left_sunday          # absolute column 0
    weeks = years * 52
    strip = build_strip(SCRIPT, min_cols=weeks + COLS + 2)

    frames = []
    t_values = list(range(0, weeks + 1, step_weeks))
    for i, t in enumerate(t_values):
        window = [row[t:t + COLS] for row in strip]
        # right-most visible column absolute index = t + COLS-1 ; its Saturday:
        right_sat = base_left_sunday + timedelta(weeks=t + COLS - 1, days=6)
        fr = render_frame(window, right_sat, t, years)
        if i == 0:
            frames.extend([fr] * hold_start)   # linger on OPEN YOUR MIND
        frames.append(fr)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=ms, loop=0, optimize=True, disposal=2)
    return out, len(frames), strip


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=10)
    ap.add_argument("--step", type=int, default=1, help="weeks advanced per frame")
    ap.add_argument("--ms", type=int, default=55)
    ap.add_argument("--open", action="store_true")
    a = ap.parse_args()
    out, n, strip = build_gif(years=a.years, step_weeks=a.step, ms=a.ms)
    print(f"wrote {out}  ({n} frames, strip width {len(strip[0])} cols, {a.years} yrs)")
    sz = os.path.getsize(out) / 1e6
    print(f"size: {sz:.1f} MB")
    if a.open:
        os.system(f'open "{out}"')

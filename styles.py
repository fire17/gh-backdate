"""
styles.py — turn a binary text mask into a shaded LEVEL grid (0..4).

Modes:
  "none"     : flat brightest (level 4). Plain, no shadow. [default]
  "drop"     : bright text + dim offset shadow (depth).
  "outline"  : bright text + dim 1px halo glow.
  "twotone"  : top rows of each letter bright (4), lower rows dim (2)
               — mimics the OpenCode PRIMARY/SECONDARY look on any font.
  "native"   : use the font's own zone grid (OpenCode two-tone) if provided.
  "twinkle"  : flat text + random star-like 0..4 shades sprinkled on the
               Sunday (row 0) and Saturday (row 6) rows to make top/bottom pop.
  "twinkle_drop" : drop shadow + the Sun/Sat twinkle border.

Randomness is SEEDED from the text so a given phrase always twinkles the same
way (reproducible — important once these become real commits).
"""

from __future__ import annotations
import random

ROWS_DEFAULT = 7


def _blank(cols, rows):
    return [[0] * cols for _ in range(rows)]


def _shift(mask, dx, dy):
    rows, cols = len(mask), len(mask[0])
    out = _blank(cols, rows)
    for y in range(rows):
        for x in range(cols):
            if mask[y][x]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    out[ny][nx] = 1
    return out


def _twinkle_rows(grid, mask, seed_text, rows_to_star=(0, -1),
                  density=0.5):
    """Sprinkle random 0..4 shades onto given rows where empty (star border)."""
    rows, cols = len(grid), len(grid[0])
    rng = random.Random(f"twinkle:{seed_text}")
    # weight toward dim stars, occasional bright
    levels = [1, 1, 1, 2, 2, 3, 4]
    for r in rows_to_star:
        rr = r if r >= 0 else rows + r
        for x in range(cols):
            if grid[rr][x] == 0 and mask[rr][x] == 0 and rng.random() < density:
                grid[rr][x] = rng.choice(levels)
    return grid


def apply_style(mask, mode="none", zone=None, seed_text="", main=4,
                shadow_level=1):
    rows, cols = len(mask), len(mask[0])
    out = _blank(cols, rows)

    if mode in ("none", "twinkle"):
        for y in range(rows):
            for x in range(cols):
                if mask[y][x]:
                    out[y][x] = main

    elif mode in ("drop", "twinkle_drop"):
        sh = _shift(mask, 1, 1)
        for y in range(rows):
            for x in range(cols):
                if mask[y][x]:
                    out[y][x] = main
                elif sh[y][x]:
                    out[y][x] = shadow_level

    elif mode == "outline":
        for y in range(rows):
            for x in range(cols):
                if mask[y][x]:
                    out[y][x] = main
        for y in range(rows):
            for x in range(cols):
                if out[y][x]:
                    continue
                if any(0 <= y+dy < rows and 0 <= x+dx < cols and mask[y+dy][x+dx]
                       for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    out[y][x] = 1

    elif mode == "twotone":
        # brightest in the top half of each lit column-run, dimmer below
        for y in range(rows):
            for x in range(cols):
                if mask[y][x]:
                    out[y][x] = 4 if y <= rows // 2 else 2

    elif mode == "native":
        for y in range(rows):
            for x in range(cols):
                if mask[y][x]:
                    if zone is not None and zone[y][x] == 2:
                        out[y][x] = 2
                    else:
                        out[y][x] = 4
    else:
        raise ValueError(f"unknown style {mode!r}")

    if mode in ("twinkle", "twinkle_drop"):
        out = _twinkle_rows(out, mask, seed_text)

    return out

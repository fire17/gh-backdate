"""
shade.py — 4-level shading for the banner (GitHub's four green tiers).

Grid cells are now integers 0..4:
    0 = empty
    1 = weakest visible   -> 1 commit   (#0e4429)
    2 = brighter          -> 3 commits  (#006d32)
    3 = brighter          -> 6 commits  (#26a641)
    4 = brightest         -> 9 commits  (#39d353)

Commit counts per level are user-defined (1/3/6/9). Because GitHub's tier
thresholds are relative to the busiest day, on a throwaway account whose only
activity is the banner, a day with 9 commits is the darkest tier and 1/3/6 land
on the progressively lighter tiers — giving true multi-shade shadows.

Shading effects build a level-grid from the binary glyph mask:
  * drop shadow  — main text at a bright level, an offset copy at a dim level
  * outline/glow — a dim halo around bright text
"""

from __future__ import annotations
from bitmapfont import render_word
from gridmap import COLS, ROWS

# level -> commits (user spec)
LEVEL_COMMITS = {0: 0, 1: 1, 2: 3, 3: 6, 4: 9}

# GitHub dark-theme tier colors, indexed by level
SHADES = {
    0: (22, 27, 34),     # #161b22 empty
    1: (14, 68, 41),     # #0e4429
    2: (0, 109, 50),     # #006d32
    3: (38, 166, 65),    # #26a641
    4: (57, 211, 83),    # #39d353
}


def _mask(text: str, cols: int = COLS, rows: int = ROWS):
    grid, tw, gap, wg = render_word(text, cols, rows)
    return grid, tw, gap, wg


def _blank(cols=COLS, rows=ROWS):
    return [[0] * cols for _ in range(rows)]


def _shift(mask, dx, dy, cols=COLS, rows=ROWS):
    out = _blank(cols, rows)
    for y in range(rows):
        for x in range(cols):
            if mask[y][x]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    out[ny][nx] = 1
    return out


def drop_shadow(text: str, main: int = 4, shadow: int = 1,
                dx: int = 1, dy: int = 1, cols=COLS, rows=ROWS):
    """Bright text with an offset dim shadow underneath. Main wins on overlap."""
    mask, tw, gap, wg = _mask(text, cols, rows)
    shadow_mask = _shift(mask, dx, dy, cols, rows)
    out = _blank(cols, rows)
    for y in range(rows):
        for x in range(cols):
            if mask[y][x]:
                out[y][x] = main
            elif shadow_mask[y][x]:
                out[y][x] = shadow
    return out, tw, gap, wg


def outline(text: str, main: int = 4, halo: int = 1, cols=COLS, rows=ROWS):
    """Bright text wrapped in a dim 1px halo (soft glow)."""
    mask, tw, gap, wg = _mask(text, cols, rows)
    out = _blank(cols, rows)
    for y in range(rows):
        for x in range(cols):
            if mask[y][x]:
                out[y][x] = main
    for y in range(rows):
        for x in range(cols):
            if out[y][x]:
                continue
            near = any(0 <= y+ddy < rows and 0 <= x+ddx < cols and mask[y+ddy][x+ddx]
                       for ddy in (-1, 0, 1) for ddx in (-1, 0, 1))
            if near:
                out[y][x] = halo
    return out, tw, gap, wg


def flat(text: str, level: int = 4, cols=COLS, rows=ROWS):
    """Single-shade banner at `level`."""
    mask, tw, gap, wg = _mask(text, cols, rows)
    out = [[level if mask[y][x] else 0 for x in range(cols)] for y in range(rows)]
    return out, tw, gap, wg


def level_stats(grid):
    counts = {L: 0 for L in range(5)}
    for row in grid:
        for v in row:
            counts[v] = counts.get(v, 0) + 1
    total_commits = sum(counts[L] * LEVEL_COMMITS[L] for L in range(5))
    return counts, total_commits


def level_ascii(grid):
    ramp = {0: "··", 1: "░░", 2: "▒▒", 3: "▓▓", 4: "██"}
    return "\n".join("".join(ramp[v] for v in row) for row in grid)

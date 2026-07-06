"""
strip.py — compose a long 7-row "tape" of words + 7-tall icons.

The tape is placed in ABSOLUTE week-space: column 0 == the leftmost column of
today's contribution window (Grid(today).left_sunday). The animation slides a
53-wide window rightward across the tape, one column per week, so the content
scrolls LEFT like a marquee and future weeks reveal new glyphs.

A SCRIPT is a list of tokens:
    ("word", "HELLO")      -> 5-tall text, vertically centered in the 7 rows
    ("icon", "smiley")     -> a 7-tall glyph from glyphs7
    ("gap",  4)            -> n blank columns

Edit SCRIPT freely. To schedule a "secret message for the future", place it at a
known column offset (see place_at()) — it will scroll into view on that week.
"""

from __future__ import annotations
from bitmapfont import GLYPHS as FONT, glyph_width, GLYPH_H
from glyphs7 import GLYPHS7, normalized, width as icon_width

ROWS = 7
FONT_Y = (ROWS - GLYPH_H) // 2  # center the 5-tall font in 7 rows -> y=1


def stamp_word(strip: list[list[int]], x: int, text: str,
               gap: int = 1, word_gap: int = 3) -> int:
    """Stamp UPPERCASE text starting at column x. Returns the next free column."""
    text = text.upper()
    prev_vis = False
    for ch in text:
        if ch == " ":
            x += word_gap
            prev_vis = False
            continue
        g = FONT.get(ch)
        if g is None:
            continue
        if prev_vis:
            x += gap
        gw = glyph_width(ch)
        for ry, rowstr in enumerate(g):
            for rx, c in enumerate(rowstr):
                if c == "#":
                    _set(strip, x + rx, FONT_Y + ry)
        x += gw
        prev_vis = True
    return x


def stamp_icon(strip: list[list[int]], x: int, name: str) -> int:
    g = normalized(name)
    for ry, rowstr in enumerate(g):
        for rx, c in enumerate(rowstr):
            if c == "#":
                _set(strip, x + rx, ry)
    return x + icon_width(name)


def _set(strip, x, y):
    if 0 <= y < ROWS and x >= 0:
        while x >= len(strip[0]):
            for row in strip:
                row.append(0)
        strip[y][x] = 1


def build_strip(script: list[tuple], min_cols: int, token_gap: int = 3,
                loop_gap: int = 8) -> list[list[int]]:
    """Render SCRIPT into a 7xN tape, cycling the script until >= min_cols."""
    strip = [[0] for _ in range(ROWS)]
    x = 0
    while x < min_cols:
        for kind, val in script:
            if kind == "word":
                x = stamp_word(strip, x, val) + token_gap
            elif kind == "icon":
                x = stamp_icon(strip, x, val) + token_gap
            elif kind == "gap":
                x += int(val)
        x += loop_gap  # gap before the script repeats
    # trim to exact width (>= min_cols)
    width = max(min_cols, len(strip[0]))
    for row in strip:
        while len(row) < width:
            row.append(0)
    return strip


# The default parade: OPEN YOUR MIND, then a long varied cycle of cool things.
SCRIPT: list[tuple] = [
    ("word", "OPEN YOUR MIND"),
    ("gap", 6),
    ("icon", "smiley"), ("gap", 4),
    ("word", "STAY"), ("word", "CURIOUS"),
    ("icon", "heart"), ("gap", 4),
    ("word", "DREAM"), ("word", "BIG"),
    ("icon", "star"), ("gap", 4),
    ("icon", "invader"), ("gap", 3), ("icon", "alien"),
    ("gap", 6),
    ("word", "HELLO"), ("word", "WORLD"),
    ("icon", "cat"), ("gap", 3), ("icon", "ghost"),
    ("gap", 6),
    ("word", "BE"), ("word", "KIND"),
    ("icon", "sun"), ("gap", 4),
    ("word", "THE"), ("word", "FUTURE"),
    ("word", "IS"), ("word", "NOW"),
    ("icon", "lightning"), ("gap", 3), ("icon", "arrow"),
    ("gap", 6),
    ("icon", "cool"), ("gap", 3), ("icon", "wink"), ("gap", 3), ("icon", "surprised"),
    ("gap", 6),
    ("word", "KEEP"), ("word", "GOING"),
    ("icon", "check"), ("gap", 4),
    ("icon", "note"), ("gap", 3), ("icon", "diamond"), ("gap", 3), ("icon", "robot"),
    ("gap", 6),
    ("word", "MADE"), ("word", "WITH"),
    ("icon", "heart"), ("gap", 8),
]

"""
bitmapfont.py — a hand-crafted 5-row-tall variable-width UPPERCASE pixel font,
purpose-built for legibility at contribution-graph resolution (7 rows tall).

All-caps is deliberate: at ~4px per character, uppercase forms with no
x-height/ascender/descender ambiguity are dramatically more legible than
mixed case. Glyphs are 5 rows tall and centered vertically in the 7-row grid.

The renderer lays glyphs left-to-right with 1px inter-glyph gaps and an
adaptive word gap, then centers the whole word in COLS x ROWS. If a phrase is
too wide it tightens the word gap, then the letter gap, so text ALWAYS fits.
"""

from __future__ import annotations

# Each glyph: list of 5 strings, '#' = lit. Width = len of a row.
GLYPHS: dict[str, list[str]] = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "F": ["###", "#..", "##.", "#..", "#.."],
    "G": ["###", "#..", "#.#", "#.#", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["#", "#", "#", "#", "#"],
    "J": ["###", "..#", "..#", "#.#", ".#."],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"],
    "P": ["##.", "#.#", "##.", "#..", "#.."],
    "Q": [".#.", "#.#", "#.#", "#.#", ".##"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#", "##", ".#", ".#", ".#"],
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "##.", "..#", "##."],
    "6": [".##", "#..", "##.", "#.#", "###"],
    "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "##."],
    "!": ["#", "#", "#", ".", "#"],
    "?": ["##.", "..#", ".#.", "...", ".#."],
    ".": ["", "", "", "", "#"],
    "-": ["...", "...", "###", "...", "..."],
    "'": ["#", "#", ".", ".", "."],
}

GLYPH_H = 5


def glyph_width(ch: str) -> int:
    g = GLYPHS.get(ch.upper())
    if g is None:
        return 0
    return max((len(r) for r in g), default=0)


def _word_layout_width(text: str, gap: int, word_gap: int) -> int:
    """Total pixel width for text at the given letter gap / word gap."""
    w = 0
    prev_visible = False
    for ch in text:
        if ch == " ":
            w += word_gap
            prev_visible = False
            continue
        gw = glyph_width(ch)
        if gw == 0:
            continue
        if prev_visible:
            w += gap
        w += gw
        prev_visible = True
    return w


def render_word(text: str, cols: int, rows: int,
                gap: int = 1, word_gap: int = 2) -> list[list[int]]:
    """Render `text` into a rows x cols binary grid, auto-fitting the width."""
    text = text.upper()

    # adaptive fit: tighten word gap, then letter gap, until it fits
    g, wg = gap, word_gap
    while _word_layout_width(text, g, wg) > cols and wg > 0:
        wg -= 1
    while _word_layout_width(text, g, wg) > cols and g > 0:
        g -= 1
    total_w = _word_layout_width(text, g, wg)

    grid = [[0] * cols for _ in range(rows)]
    x0 = max(0, (cols - total_w) // 2)
    y0 = max(0, (rows - GLYPH_H) // 2)

    x = x0
    prev_visible = False
    for ch in text:
        if ch == " ":
            x += wg
            prev_visible = False
            continue
        glyph = GLYPHS.get(ch)
        if glyph is None:
            continue
        gw = glyph_width(ch)
        if prev_visible:
            x += g
        for ry, rowstr in enumerate(glyph):
            for rx, c in enumerate(rowstr):
                if c == "#" and 0 <= x + rx < cols and 0 <= y0 + ry < rows:
                    grid[y0 + ry][x + rx] = 1
        x += gw
        prev_visible = True

    return grid, total_w, g, wg


def fits(text: str, cols: int, gap: int = 1, word_gap: int = 1) -> bool:
    return _word_layout_width(text.upper(), gap, word_gap) <= cols

"""
smallfonts.py — 4-tall and 3-tall micro pixel fonts, for stacking TWO text lines
inside the 7-row contribution window (big line rows 0–3, small line rows 4–6).

Partial by design: glyphs exist for the phrases we ship; extend as needed.
"""
from __future__ import annotations

FONT4 = {  # 4-tall "bigger" line
    "O": ["###", "#.#", "#.#", "###"],
    "P": ["###", "#.#", "###", "#.."],
    "E": ["###", "#..", "##.", "###"],
    "N": ["#..#", "##.#", "#.##", "#..#"],
    "Y": ["#.#", "#.#", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "###"],
    "R": ["###", "#.#", "##.", "#.#"],
    "M": ["#...#", "##.##", "#.#.#", "#...#"],
    "I": ["#", "#", "#", "#"],
    "D": ["##.", "#.#", "#.#", "##."],
}

FONT3 = {  # 3-tall "smaller" line
    "M": ["#...#", "##.##", "#...#"],
    "A": [".#.", "###", "#.#"],
    "D": ["##.", "#.#", "##."],
    "E": ["###", "##.", "###"],
    "W": ["#...#", "#.#.#", ".#.#."],
    "I": ["#", "#", "#"],
    "T": ["###", ".#.", ".#."],
    "H": ["#.#", "###", "#.#"],
    "♥": [".#.#.", "#####", "..#.."],
}


def stamp(grid: list[list[int]], font: dict, x: int, y: int, text: str,
          gap: int = 1, word_gap: int = 2, level: int = 1) -> int:
    """Stamp text at (x, y); '.'=off '#'=on. Returns next free column."""
    first = True
    for ch in text.upper():
        if ch == " ":
            x += word_gap
            first = True
            continue
        g = font.get(ch)
        if g is None:
            continue
        if not first:
            x += gap
        for ry, row in enumerate(g):
            for rx, c in enumerate(row):
                if c == "#":
                    grid[y + ry][x + rx] = level
        x += len(g[0])
        first = False
    return x


def text_width(font: dict, text: str, gap: int = 1, word_gap: int = 2) -> int:
    w, first = 0, True
    for ch in text.upper():
        if ch == " ":
            w += word_gap
            first = True
            continue
        g = font.get(ch)
        if g is None:
            continue
        w += (0 if first else gap) + len(g[0])
        first = False
    return w


def two_lines(top: str = "OPEN YOUR MIND", bottom: str = "MADE WITH ♥",
              cols: int = 53) -> list[list[int]]:
    """The experimental window: 4-tall top-LEFT line + 3-tall bottom-RIGHT line."""
    grid = [[0] * cols for _ in range(7)]
    stamp(grid, FONT4, 0, 0, top)                                   # rows 0-3, left
    bw = text_width(FONT3, bottom)
    stamp(grid, FONT3, max(0, cols - bw), 4, bottom)                # rows 4-6, right
    return grid


if __name__ == "__main__":
    g = two_lines()
    print(f'top width {text_width(FONT4, "OPEN YOUR MIND")} · '
          f'bottom width {text_width(FONT3, "MADE WITH ♥")} · cols 53')
    for row in g:
        print("".join("█" if v else "·" for v in row))

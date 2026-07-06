#!/usr/bin/env python3
"""
banner.py — render a GitHub contribution-graph banner and (optionally) plan the
backdated commits that paint it.

Examples:
    python3 banner.py "Open Your Mind"                       # multigradient ON (drop shadow)
    python3 banner.py "Open Your Mind" --multigradient off   # flat brightest green
    python3 banner.py "Open Your Mind" --style outline
    python3 banner.py "Hello" --multigradient on --style drop-shadow --open

--multigradient on   -> 4-shade shading (levels 1/3/6/9 commits)  [default]
--multigradient off  -> single flat shade (level 4 = 9 commits)
"""

from __future__ import annotations
import argparse
import os
from datetime import date

from gridmap import Grid, COLS, ROWS
from shade import drop_shadow, outline, flat, level_stats, level_ascii, LEVEL_COMMITS
from preview import render_png


def build_grid(text: str, multigradient: bool, style: str, level: int):
    if not multigradient:
        return flat(text, level=level)
    if style == "outline":
        return outline(text, main=4, halo=1)
    if style == "flat":
        return flat(text, level=level)
    return drop_shadow(text, main=4, shadow=1, dx=1, dy=1)  # default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--multigradient", choices=["on", "off"], default="on")
    ap.add_argument("--style", choices=["drop-shadow", "outline", "flat"],
                    default="drop-shadow", help="shading style when multigradient is on")
    ap.add_argument("--level", type=int, default=4, choices=[1, 2, 3, 4],
                    help="shade level for flat / multigradient-off")
    ap.add_argument("--outdir", default="/Users/magic/Creations/Lively/gh-banner/out")
    ap.add_argument("--open", action="store_true", help="open the PNG when done")
    args = ap.parse_args()

    mg = args.multigradient == "on"
    grid, tw, gap, wg = build_grid(args.text, mg, args.style, args.level)

    g = Grid(date.today())
    counts, total_commits = level_stats(grid)

    print(f'=== "{args.text}"  multigradient={args.multigradient}  '
          f'style={args.style if mg else "flat"} ===')
    print(f"grid {COLS}x{ROWS}  width {tw}/{COLS}  gap={gap} word_gap={wg}")
    print("corners:")
    for name, dd in g.corners().items():
        print(f"  {name:13s}: {dd} ({dd.strftime('%A')})")
    print("\nshade tiers (cells x commits/cell):")
    for L in range(1, 5):
        if counts[L]:
            print(f"  L{L}: {counts[L]:3d} cells x {LEVEL_COMMITS[L]} = "
                  f"{counts[L]*LEVEL_COMMITS[L]} commits")
    print(f"  TOTAL commits to paint: {total_commits}")
    print("\n" + level_ascii(grid) + "\n")

    os.makedirs(args.outdir, exist_ok=True)
    tag = f"multigradient_{args.style}" if mg else "flat"
    safe = "".join(c if c.isalnum() else "_" for c in args.text.lower())
    out = f"{args.outdir}/{safe}__{tag}.png"
    title = (f'"{args.text}"  —  multigradient {args.multigradient}'
             f'{"  ("+args.style+")" if mg else ""}  —  {total_commits} commits')
    render_png(grid, out, ref_day=g.today, title=title)
    print("wrote", out)
    if args.open:
        os.system(f'open "{out}"')


if __name__ == "__main__":
    main()

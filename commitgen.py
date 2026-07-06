"""
commitgen.py — turn a lit-cell grid into backdated commits that paint the
banner onto a GitHub contributions graph.

For every LIT cell (col,row) we emit `intensity` empty commits authored on that
cell's date (from gridmap). Empty commits count toward contributions and leave
no file churn. Uniform intensity across all lit cells makes every square the
SAME (darkest) shade, since GitHub's tiers are relative to the busiest day —
on a throwaway account whose only activity is the banner, every lit day == max.

Future cells (the current week's not-yet-happened days) are allowed: git will
happily author a commit with a future date, and GitHub renders it.

SAFE BY DEFAULT: dry_run=True just prints the plan. Real runs need an explicit
repo + confirmation and are meant for a THROWAWAY alt account.
"""

from __future__ import annotations
import os
import subprocess
from datetime import date, datetime, timedelta
from gridmap import Grid, COLS, ROWS
from shade import LEVEL_COMMITS


def plan_from_grid(grid: list[list[int]], ref_day: date, intensity: int | None = None):
    """
    Yield (date, n_commits) for every lit cell, left->right, top->bottom.

    Cell values are shade levels 0..4; each maps to its commit count via
    LEVEL_COMMITS (1/3/6/9). Pass `intensity` to override with a uniform count
    for every lit cell (legacy single-shade behaviour).
    """
    g = Grid(ref_day)
    for col in range(COLS):
        for row in range(ROWS):
            level = grid[row][col]
            if level:
                n = intensity if intensity is not None else LEVEL_COMMITS[level]
                yield g.date_at(col, row), n


def summarize(grid, ref_day: date, intensity: int | None = None):
    cells = list(plan_from_grid(grid, ref_day, intensity))
    lit = len(cells)
    total = sum(n for _, n in cells)
    dates = [d for d, _ in cells]
    return {
        "lit_cells": lit,
        "commits_per_cell": intensity if intensity is not None else "by-level(1/3/6/9)",
        "total_commits": total,
        "first_date": min(dates).isoformat() if dates else None,
        "last_date": max(dates).isoformat() if dates else None,
        "future_cells": sum(1 for d in dates if d > ref_day),
    }


def _run(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, env=env, check=True,
                          capture_output=True, text=True)


def paint(grid, ref_day: date, repo_dir: str,
          author_name: str, author_email: str,
          intensity: int | None = None, dry_run: bool = True,
          branch: str = "main", noon_hour: int = 12) -> dict:
    """
    Create the backdated commits in `repo_dir` (an existing git repo on `branch`).
    dry_run=True prints the plan and makes NO commits.
    """
    summary = summarize(grid, ref_day, intensity)
    if dry_run:
        summary["dry_run"] = True
        return summary

    made = 0
    for cell_date, n in plan_from_grid(grid, ref_day, intensity):
        for k in range(n):
            # spread timestamps across the day so each commit is distinct
            ts = datetime(cell_date.year, cell_date.month, cell_date.day,
                          (noon_hour + k) % 24, (k * 7) % 60, (k * 13) % 60)
            iso = ts.strftime("%Y-%m-%dT%H:%M:%S")
            env = dict(os.environ,
                       GIT_AUTHOR_DATE=iso, GIT_COMMITTER_DATE=iso,
                       GIT_AUTHOR_NAME=author_name, GIT_AUTHOR_EMAIL=author_email,
                       GIT_COMMITTER_NAME=author_name, GIT_COMMITTER_EMAIL=author_email)
            _run(["git", "commit", "--allow-empty", "-q",
                  "-m", f"paint {cell_date.isoformat()} #{k+1}"], repo_dir, env)
            made += 1
    summary["dry_run"] = False
    summary["commits_made"] = made
    return summary


if __name__ == "__main__":
    import sys, json
    from shade import drop_shadow
    text = sys.argv[1] if len(sys.argv) > 1 else "Open Your Mind"
    grid, tw, gap, wg = drop_shadow(text)
    print(f'phrase "{text}"  width {tw}/{COLS}  gap={gap} word_gap={wg}')
    print(json.dumps(summarize(grid, date.today()), indent=2))
    print("\n(dry plan only — pass a real repo to paint())")

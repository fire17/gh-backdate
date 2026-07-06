#!/usr/bin/env python3
"""
backdate.py — QUICK FUNCTIONS: write anything onto the contribution graph,
at ANY time window. The one-liner layer over the whole toolkit.

    from backdate import write, write_script, plan

    plan("HELLO WORLD", start="2019-01-06")            # dry summary, no repo needed
    write("HELLO WORLD", start="2019-01-06",
          repo="~/code/myrepo", dry_run=False)         # paint a past window
    write("SEE YOU IN 2030", start="2030-03-03",
          repo="...", dry_run=False)                   # future works too — git+GitHub allow it
    write_script(years=10, repo="...", dry_run=False)  # the full 10-year parade (strip.SCRIPT)

Anchoring: the tape's column 0 is pinned to the SUNDAY on/just before `start`.
Every lit cell (col,row) becomes commits dated start_sunday + col weeks + row days.
Rows are Sunday(0)..Saturday(6) — exactly GitHub's contribution matrix.

CLI:
    python3 backdate.py "HELLO" --start 2019-01-06 [--repo DIR --paint] [--intensity N]
    python3 backdate.py --script --years 10 --repo DIR --paint
"""
from __future__ import annotations
import os
import subprocess
from datetime import date, datetime, timedelta

from strip import build_strip, stamp_word, SCRIPT
from shade import LEVEL_COMMITS

ROWS = 7


def _sunday_on_or_before(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)  # Mon=0..Sun=6 -> Sun


def _as_date(d) -> date:
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d))


def text_strip(text: str) -> list[list[int]]:
    """A minimal tape holding just `text` (5-tall font centered in 7 rows)."""
    strip = [[] for _ in range(ROWS)]
    end = stamp_word(strip, 0, text)
    for row in strip:
        while len(row) < end:
            row.append(0)
    return strip


def cells(strip: list[list[int]], start_sunday: date):
    """Yield (date, level) for every lit cell of the tape, anchored at start_sunday."""
    for col in range(len(strip[0])):
        for row in range(ROWS):
            level = strip[row][col]
            if level:
                yield start_sunday + timedelta(weeks=col, days=row), level


def summarize(strip, start_sunday: date, intensity: int | None = None) -> dict:
    plan_ = [(d, intensity or LEVEL_COMMITS[min(lv, 4)]) for d, lv in cells(strip, start_sunday)]
    dates = [d for d, _ in plan_]
    return {
        "columns": len(strip[0]), "lit_cells": len(plan_),
        "total_commits": sum(n for _, n in plan_),
        "first_date": min(dates).isoformat() if dates else None,
        "last_date": max(dates).isoformat() if dates else None,
        "future_cells": sum(1 for d in dates if d > date.today()),
    }


def _commit(repo: str, when: datetime, msg: str, name: str, email: str):
    iso = when.strftime("%Y-%m-%dT%H:%M:%S")
    env = dict(os.environ,
               GIT_AUTHOR_DATE=iso, GIT_COMMITTER_DATE=iso,
               GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email,
               GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email)
    subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", msg],
                   cwd=os.path.expanduser(repo), env=env, check=True,
                   capture_output=True, text=True)


def paint_strip(strip, start_sunday: date, repo: str, name: str, email: str,
                intensity: int | None = None, dry_run: bool = True,
                noon_hour: int = 12) -> dict:
    """The engine: tape + anchor date + repo -> backdated empty commits."""
    summary = summarize(strip, start_sunday, intensity)
    summary["dry_run"] = dry_run
    if dry_run:
        return summary
    made = 0
    for cell_date, level in cells(strip, start_sunday):
        n = intensity or LEVEL_COMMITS[min(level, 4)]
        for k in range(n):
            ts = datetime(cell_date.year, cell_date.month, cell_date.day,
                          (noon_hour + k) % 24, (k * 7) % 60, (k * 13) % 60)
            _commit(repo, ts, f"paint {cell_date.isoformat()} #{k + 1}", name, email)
            made += 1
    summary["commits_made"] = made
    return summary


def _git_identity(repo: str) -> tuple[str, str]:
    def cfg(key):
        r = subprocess.run(["git", "config", key], cwd=os.path.expanduser(repo),
                           capture_output=True, text=True)
        return r.stdout.strip()
    return cfg("user.name") or "gh-backdate", cfg("user.email")


def write(text: str, start, repo: str = ".", *, intensity: int | None = None,
          dry_run: bool = True, name: str = None, email: str = None) -> dict:
    """Write `text` starting the week of `start` (date or 'YYYY-MM-DD')."""
    n, e = _git_identity(repo)
    return paint_strip(text_strip(text), _sunday_on_or_before(_as_date(start)),
                       repo, name or n, email or e, intensity, dry_run)


def write_script(script=None, *, years: int = 10, end=None, repo: str = ".",
                 intensity: int | None = None, dry_run: bool = True,
                 name: str = None, email: str = None) -> dict:
    """Paint a full parade (default strip.SCRIPT) across the LAST `years` years,
    ending at the current week — i.e. the '10-year banner'."""
    end_sunday = _sunday_on_or_before(_as_date(end) if end else date.today())
    strip = build_strip(script or SCRIPT, min_cols=years * 52)
    start_sunday = end_sunday - timedelta(weeks=len(strip[0]) - 1)
    n, e = _git_identity(repo)
    return paint_strip(strip, start_sunday, repo, name or n, email or e,
                       intensity, dry_run)


def plan(text: str, start) -> dict:
    """Dry summary of write() with no repo at all."""
    return summarize(text_strip(text), _sunday_on_or_before(_as_date(start)))


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser(description="write anything, any time window")
    ap.add_argument("text", nargs="?", default="HELLO WORLD")
    ap.add_argument("--start", help="YYYY-MM-DD anchor (week of)")
    ap.add_argument("--script", action="store_true", help="use the full strip.SCRIPT parade")
    ap.add_argument("--years", type=int, default=10)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--intensity", type=int, default=None, help="uniform commits/cell (default: by-level 1/3/6/9)")
    ap.add_argument("--paint", action="store_true", help="actually commit (default: dry-run)")
    a = ap.parse_args()
    if a.script:
        out = write_script(years=a.years, repo=a.repo, intensity=a.intensity, dry_run=not a.paint)
    else:
        start = a.start or date.today().isoformat()
        out = write(a.text, start, a.repo, intensity=a.intensity, dry_run=not a.paint)
    print(json.dumps(out, indent=2))

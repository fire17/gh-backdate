#!/usr/bin/env python3
"""
modes.py — canvas modes for the painted contribution graph. The DEFAULT banner
is always remembered (its SHA in ~/.config/gh-alt/canvas-state.json); every mode
is a force-push away, and temporary modes revert THEMSELVES via a detached
process — no agent, no session, no cron needed.

    modes.py status                              # where are we vs default
    modes.py ghost "YO YO OMER :heart:" -m 10    # temp text, auto-revert in 10 min
    modes.py starry                              # random noise, all 5 shades, permanent
    modes.py starry --density 3 -m 10            # denser stars, auto-revert
    modes.py revert                              # back to default NOW

Starry density: level 0..4 drawn per day; at density 1 all five are equally
likely (a day off ~1 in 5). Density d shrinks the zero-weight to 1/d — at d=4
a dark day is ~1 in 17, rare but possible. Seeded runs reproducible via --seed.
"""
from __future__ import annotations
import argparse
import json
import os
import random
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from backdate import paint_strip, _sunday_on_or_before  # noqa: E402
from strip import stamp_word, stamp_icon                # noqa: E402

STATE = Path.home() / ".config/gh-alt/canvas-state.json"
TOKEN = Path.home() / ".config/gh-alt/token"
LOG = Path.home() / ".config/gh-alt/modes.log"
COLS, ROWS = 53, 7


def state() -> dict:
    return json.loads(STATE.read_text())


def sh(args, cwd, **kw):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True, **kw)


def push_sha(sha: str, note: str):
    st, tok = state(), TOKEN.read_text().strip()
    for remote in st["remotes"]:
        sh(["git", "push", "--force", f"https://x-access-token:{tok}@github.com/{remote}.git",
            f"{sha}:refs/heads/main"], st["clone"])
    with LOG.open("a") as f:
        f.write(f"{date.today().isoformat()} push {sha[:10]} ({note})\n")


def window_start() -> date:
    """Left column of the CURRENT 53-week window (a Sunday)."""
    from gridmap import Grid
    return Grid(date.today()).left_sunday


def ghost_grid(text: str) -> list[list[int]]:
    """5-tall text (+ :heart: icons) centered in the 7 rows, clipped to 53 cols."""
    strip = [[] for _ in range(ROWS)]
    x = 0
    for token in text.replace(":heart:", " \x00 ").split():
        if token == "\x00":
            x = stamp_icon(strip, x, "heart") + 2
        else:
            x = stamp_word(strip, x, token) + 3
    for row in strip:
        while len(row) < COLS:
            row.append(0)
    return [row[:COLS] for row in strip]


def starry_grid(density: float, seed=None) -> list[list[int]]:
    rng = random.Random(seed)
    weights = [1.0 / max(density, 0.01), 1, 1, 1, 1]     # zero-weight shrinks with density
    return [[rng.choices(range(5), weights=weights)[0] for _ in range(COLS)]
            for _ in range(ROWS)]


def repaint(grid, note: str, intensity=None) -> str:
    """Rebuild branch = base + this window paint; return new sha (NOT yet pushed)."""
    st = state()
    sh(["git", "reset", "--hard", "-q", st["base_sha"]], st["clone"])
    name, email = st["author"].rsplit(" <", 1)
    paint_strip(grid, window_start(), st["clone"], name, email.rstrip(">"),
                intensity=intensity, dry_run=False)
    return sh(["git", "rev-parse", "HEAD"], st["clone"]).stdout.strip()


def schedule_revert(minutes: float):
    """Detached self-reverter: survives this process, needs no agent."""
    st = state()
    script = (f'sleep {int(minutes * 60)}; cd "{st["clone"]}"; '
              f'TOK=$(cat "{TOKEN}"); '
              + " ; ".join(
                  f'git push --force "https://x-access-token:$TOK@github.com/{r}.git" '
                  f'{st["default_sha"]}:refs/heads/main' for r in st["remotes"])
              + f' ; git reset --hard -q {st["default_sha"]}'
              + f' ; echo "$(date +%FT%T) auto-reverted to default" >> "{LOG}"')
    subprocess.Popen(["nohup", "sh", "-c", script],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("ghost");  g.add_argument("text")
    g.add_argument("-m", "--minutes", type=float, default=10)
    g.add_argument("--forever", action="store_true")
    s = sub.add_parser("starry"); s.add_argument("--density", type=float, default=1.0)
    s.add_argument("-m", "--minutes", type=float, default=0, help="0 = permanent")
    s.add_argument("--seed", type=int, default=None)
    sub.add_parser("revert"); sub.add_parser("status")
    a = ap.parse_args()

    if a.cmd == "status":
        st = state()
        head = sh(["git", "rev-parse", "HEAD"], st["clone"]).stdout.strip()
        print(f"default {st['default_sha'][:10]} · local HEAD {head[:10]} · "
              f"{'ON DEFAULT' if head == st['default_sha'] else 'MODE ACTIVE (or reverted remotely)'}")
        return
    if a.cmd == "revert":
        st = state()
        sh(["git", "reset", "--hard", "-q", st["default_sha"]], st["clone"])
        push_sha(st["default_sha"], "manual revert")
        print(f"reverted to default {st['default_sha'][:10]}")
        return
    if a.cmd == "ghost":
        sha = repaint(ghost_grid(a.text), f"ghost: {a.text}", intensity=9)
        push_sha(sha, f"ghost {a.text!r}")
        if not a.forever:
            schedule_revert(a.minutes)
        print(f"ghost live ({sha[:10]})" + ("" if a.forever else
              f" — auto-reverts to default in {a.minutes:g} min (detached, no agent needed)"))
        return
    if a.cmd == "starry":
        sha = repaint(starry_grid(a.density, a.seed), f"starry d={a.density}")
        push_sha(sha, f"starry density={a.density}")
        if a.minutes:
            schedule_revert(a.minutes)
        print(f"starry night live ({sha[:10]}), density {a.density:g}"
              + (f" — auto-reverts in {a.minutes:g} min" if a.minutes else " — permanent (modes.py revert to undo)"))


if __name__ == "__main__":
    main()

"""
gridmap.py — GitHub contribution-graph date <-> (col,row) mapping.

The GitHub contributions matrix is a grid of 53 columns x 7 rows:

  * Each COLUMN is one calendar week.
  * Rows run top->bottom = Sunday(0) .. Saturday(6).  (GitHub weeks start Sunday.)
  * The RIGHTMOST column (col = COLS-1) is the CURRENT week — the week that
    contains today. Its top cell is the current week's Sunday.
  * The LEFTMOST column (col 0) is 52 weeks earlier.

Worked example, reference day = Mon 2026-07-06 (verified against the user's spec):
    top-right    (col52,row0) = Sun 2026-07-05   <- current week's Sunday
    bottom-right (col52,row6) = Sat 2026-07-11   <- current week's Saturday (future ok)
    top-left     (col0, row0) = Sun 2025-07-06
    bottom-left  (col0, row6) = Sat 2025-07-12

The bottom-right cells can be in the FUTURE relative to today (the current week
isn't over yet). Commits can still be authored with those future dates.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta

COLS = 53          # GitHub renders 53 week-columns
ROWS = 7           # Sun..Sat


def current_week_sunday(today: date | None = None) -> date:
    """Sunday of the week that contains `today` (defaults to date.today())."""
    if today is None:
        today = date.today()
    # Python weekday(): Mon=0..Sun=6  ->  days since Sunday = (weekday()+1) % 7
    return today - timedelta(days=(today.weekday() + 1) % 7)


@dataclass(frozen=True)
class Grid:
    """The concrete date grid for a given reference day."""
    today: date
    cols: int = COLS
    rows: int = ROWS

    @property
    def right_sunday(self) -> date:
        """Top cell of the rightmost (current) column."""
        return current_week_sunday(self.today)

    @property
    def left_sunday(self) -> date:
        """Top cell of the leftmost column = right_sunday - (cols-1) weeks."""
        return self.right_sunday - timedelta(weeks=self.cols - 1)

    def date_at(self, col: int, row: int) -> date:
        """Date at grid position. col 0..cols-1 (left->right), row 0..6 (Sun..Sat)."""
        if not (0 <= col < self.cols):
            raise IndexError(f"col {col} out of range 0..{self.cols - 1}")
        if not (0 <= row < self.rows):
            raise IndexError(f"row {row} out of range 0..{self.rows - 1}")
        return self.left_sunday + timedelta(weeks=col, days=row)

    def corners(self) -> dict[str, date]:
        return {
            "top_left": self.date_at(0, 0),
            "bottom_left": self.date_at(0, self.rows - 1),
            "top_right": self.date_at(self.cols - 1, 0),
            "bottom_right": self.date_at(self.cols - 1, self.rows - 1),
        }

    def is_future(self, col: int, row: int, today: date | None = None) -> bool:
        return self.date_at(col, row) > (today or self.today)


if __name__ == "__main__":
    import sys
    ref = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    g = Grid(ref)
    print(f"reference day : {ref} ({ref.strftime('%A')})")
    print(f"grid          : {g.cols} cols x {g.rows} rows")
    for name, d in g.corners().items():
        print(f"  {name:13s}: {d} ({d.strftime('%A')})")

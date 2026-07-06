# LEARNINGS — everything this project taught us (verified, not vibed)

Harvested from the build sessions (2026-07-06): the contribution-graph mechanics,
the rendering math, and the process lessons. Each entry was observed live.

## The contribution graph, precisely

1. **The matrix is 53×7.** Column = week, rightmost column = the *current* week.
   Rows top→bottom are **Sunday(0)…Saturday(6)**. `gridmap.Grid(today)` derives
   every cell's date; verified corners for reference Monday 2026-07-06:
   top-left `Sun 2025-07-06` · bottom-right `Sat 2026-07-11`.
2. **Empty commits count.** `git commit --allow-empty` with `GIT_AUTHOR_DATE` +
   `GIT_COMMITTER_DATE` set paints a day with zero file churn. A repo full of
   them is a perfectly valid paintbrush.
3. **Backdating is unlimited; future-dating works too.** git accepts any
   author/committer date (this repo's banner starts 2014) and GitHub happily
   renders commits dated in the future — the current week's not-yet-happened
   days can already be lit.
4. **Shading is RELATIVE.** GitHub's 4 green tiers scale to your busiest day.
   Levels map to commits-per-day `1/3/6/9` (`shade.LEVEL_COMMITS`) — but on an
   active account a 1-commit day is nearly invisible; paint with high intensity
   (`--intensity 9`) to hit the top tier. On a throwaway account whose only
   activity is the banner, every lit day == max shade automatically.
5. **Contributions require**: author email verified on the GitHub account +
   commits on the **default branch** of a standalone (non-fork) repo. Delete the
   repo and the graph recalculates — the art is fully reversible.

## Rendering & typography in a 7-row universe

6. **5-tall fonts win.** A 5-tall variable-width pixel font centered in the
   7 rows (y=1) leaves breathing room; 7-tall glyphs (`glyphs7`) are for icons.
   Real TTFs (Bodoni/Baskerville/DIN/Times/Georgia) rasterized down to 7px
   (`textrender.py`, `fonts.py`) are legible but chunkier — see `out/COMPARISON.png`.
7. **Shadows need levels.** Drop-shadow / outline / two-tone / twinkle styles
   (`shade.py`, `styles.py`) only read because the 4 tiers exist — a flat
   single-shade banner loses all depth (`out/OPTIONS.png` shows every combo).
8. **The tape abstraction scales time.** A 7-row strip of arbitrary width in
   absolute week-space (`strip.py`) turns "one year of graph" into "a marquee
   across a decade" — slide a 53-wide window along it (`animate.py`) and you
   get the 10-year scroll GIF; anchor it at any Sunday (`backdate.py`) and you
   can WRITE AT ANY TIME WINDOW, past or future.

## Process lessons (paid for in real defects)

9. **Verbatim beats retyping — for pixels too.** Hand-transcribing box-drawing
   output corrupted it twice upstream of this repo; the fix was a renderer that
   *asserts* every line's display width before printing. Same law here: emit
   programmatically, paste byte-for-byte, never "fix" output by hand.
10. **Emoji width is a two-column lie with exceptions.** Most emoji are 2 cols
    in monospace, but narrow chars + U+FE0F (like ▶️) are forced wide — width
    math must be *sequence-aware* or borders bend. (Cousin of the GitHub-anchor
    war story: invisible variation selectors survive in rendered anchor ids.)
11. **Dry-run by default, always.** `commitgen`/`backdate` print a full plan
    (dates, cell count, total commits, future cells) before any repo is touched.
    Sizing the 10-year parade *before* painting is what made an 11k-commit run
    a decision instead of an accident.
12. **Recompute from today, never hardcode.** Every date derives from
    `date.today()` at run time — the same banner command stays correct forever.
13. **Preview = trust.** `preview.py` renders the exact GitHub dark-theme cell
    geometry (rounded 12px cells, month/day labels, Less→More legend) so what
    you approve is what gets painted.

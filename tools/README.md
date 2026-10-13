# tools

Helpers for working on the cat. None of them are needed to run her.

| Script | What it does |
|---|---|
| `gen_md.py` | Rebuilds `KOCICKA.md`, the all-in-one Czech guide with the real `kocicka.py` source embedded, so the two never drift. Run it after every change to `kocicka.py`. |
| `pose.py` | Opens a window with every pose side by side for six seconds, to check a drawing change at a glance. `preview.png` was made from it. |

Run both from the repo root: `python tools/gen_md.py`, `python tools/pose.py`.

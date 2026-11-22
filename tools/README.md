# tools

Helpers for working on the cat. None of them are needed to run her.

| Script | What it does |
|---|---|
| `gen_md.py` | Rebuilds `KOCICKA.md`, the all-in-one Czech guide with the real `kocicka.py` source embedded, so the two never drift. Run it after every change to `kocicka.py`. |
| `pose.py` | Opens a window with every pose side by side for six seconds, to check a drawing change at a glance. `preview.png` was made from it. With `break` it shows the hourly break sign mid-countdown instead, which is where `break.png` came from. |

| `sprites.py` | Cuts the new look out of the ChatGPT sheets in `art/` (green screen, one scale for every sheet, one shared palette) and rewrites the `SPRITES` table at the bottom of `kocicka.py`. Needs Pillow, unlike everything else here. |

`pose.py` also takes `classic` (the classic look) and `dressed` (bow, hat, a grey coat
on a mint cart).

Run them from the repo root: `python tools/gen_md.py`, `python tools/pose.py`.

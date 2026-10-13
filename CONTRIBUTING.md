# Contributing

Pull requests welcome. She is meant to be easy to work on.

## The one rule that matters

**Edit `kocicka.py`. Never edit `KOCICKA.md`.**

`KOCICKA.md` is the all-in-one version for sending to people who do not want
to deal with GitHub - it is the whole README plus the whole source in one
file, and it is **generated** by `tools/gen_md.py`. If you edit it directly, the
next regeneration silently throws your change away.

After changing `kocicka.py`, run:

```
python tools/gen_md.py
```

and commit both files together.

## Before you open a PR

```
python -m unittest discover -s tests
ruff check .
```

`tests/` is where the checking lives: how work time is counted, when breaks
start, wait, get skipped or snoozed, what a click does and where, the day
rolling over at midnight, her memory on disk, where she stands on screen, the
Windows calls (against a fake `user32`), and that every pose draws the parts
it should. Most of the app logic sits in the `Companion` class, which has no
tkinter in it, so it is tested without a display. The tests are plain
standard library, no pytest needed. Add a test for whatever you changed.

`python kocicka.py --selftest` runs a tiny smoke check that needs only the
one file (so someone with just `KOCICKA.md` can run it), then the `tests/`
suite if it sits next to her. `ruff` is the one non-stdlib tool, and only for
linting; CI pins its version. CI runs everything on Windows, macOS and Linux,
and fails if `KOCICKA.md` is out of date.

**If you changed anything she draws**, also run:

```
python tools/pose.py
```

It renders every pose side by side in one window. Look at it. Drawing bugs
are almost always relative - something is too far from something else, or
drawn in the wrong order - and they are invisible one pose at a time. This
caught three real bugs that the self-test happily passed.

## House style

- **Standard library only.** No pip installs, ever. That constraint is the
  point: anyone with Python can run her, with no setup and nothing to trust.
- **One file** for the cat. `tools/gen_md.py` and `tools/pose.py` are tools, not part
  of her.
- Keep it boring and readable. She is a toy that people should be able to
  open in Notepad and understand.
- Anything platform-specific must degrade quietly, not crash. See
  `idle_seconds()`, `fullscreen_in_front()` and `work_area()` for the
  pattern - they return a safe default when the Windows APIs are not there.
- Every word she shows goes in `STRINGS`. A test fails if Czech turns up
  anywhere else in the file.

## Good first contributions

- **Translations.** Everything she shows is in the `STRINGS` table, all in
  Czech right now and addressed to a woman. An English table in her voice
  (not a word-for-word translation) would roughly double who can use her;
  it also needs a small way to pick the language, which does not exist yet.
- **macOS and Linux.** Transparent backgrounds, idle detection, fullscreen
  detection and the taskbar position are Windows-only today.
- **More poses.** They are self-contained: add a state to `TRICKS`, give it
  a duration in `DURATION`, draw it in `draw()`, and check it on the pose
  sheet.
- **A recording.** The README has stills of every pose and of the break sign,
  but an animated GIF of her rolling around would show her off better.

## What she should not become

She works because she is quiet most of the time and says something only when
it is worth saying. Features that make her talk more, or that turn her into a
task manager or a dashboard, make her worse. The best changes are the ones
that make her more relevant, not more present.

No sound. Somebody will have her open on a call.

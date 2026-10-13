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
python kocicka.py --selftest
python -m unittest discover -s tests
```

`--selftest` is her built-in check, a single function at the bottom of the
file, so even someone with only `KOCICKA.md` can run it. `tests/` covers the
rest: how work time is counted, when breaks start and end, a hand-edited
`kocka.json`, and a smoke test that every pose draws. Both are plain standard
library, no pytest needed. Add a test for whatever you changed. CI runs all of
it on Windows, macOS and Linux, and fails if `KOCICKA.md` is out of date.

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
  `idle_seconds()` and `sharing_screen()` for the pattern - they return a
  safe default when the Windows APIs are not there.

## Good first contributions

- **Translations.** Everything she says is in `LINES`, `MEOWS`,
  `HAIRBALL_SAYS`, `BUTT_SAYS`, `BACK_SAYS`, `PAUSE_COACH` and `END_COACH`,
  all in Czech right now. English would roughly double who can use her.
- **macOS and Linux.** Transparent backgrounds, idle detection and
  fullscreen detection are Windows-only today.
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

# Contributing

Pull requests welcome. She is meant to be easy to work on.

## The one rule that matters

**Edit `kocicka.py`. Never edit `KOCICKA.md`.**

`KOCICKA.md` is the all-in-one version for sending to people who do not want
to deal with GitHub - it is the whole README plus the whole source in one
file, and it is **generated** by `_gen_md.py`. If you edit it directly, the
next regeneration silently throws your change away.

After changing `kocicka.py`, run:

```
python _gen_md.py
```

and commit both files together.

## Before you open a PR

```
python kocicka.py --selftest
```

If it prints `ok`, the logic is fine. Add an assert for whatever you changed -
there is no test framework and there does not need to be one, the whole suite
is a single function at the bottom of the file.

**If you changed anything she draws**, also run:

```
python _pose.py
```

It renders every pose side by side in one window. Look at it. Drawing bugs
are almost always relative - something is too far from something else, or
drawn in the wrong order - and they are invisible one pose at a time. This
caught three real bugs that the self-test happily passed.

## House style

- **Standard library only.** No pip installs, ever. That constraint is the
  point: anyone with Python can run her, with no setup and nothing to trust.
- **One file** for the cat. `_gen_md.py` and `_pose.py` are tools, not part
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
- **A recording.** The README badly needs an animated GIF of her rolling
  around and holding up the break sign.

## What she should not become

She works because she is quiet most of the time and says something only when
it is worth saying. Features that make her talk more, or that turn her into a
task manager or a dashboard, make her worse. The best changes are the ones
that make her more relevant, not more present.

No sound. Somebody will have her open on a call.

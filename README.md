# Kočička

[![CI](https://github.com/terezakohutova/kocicka/actions/workflows/ci.yml/badge.svg)](https://github.com/terezakohutova/kocicka/actions/workflows/ci.yml)

A desktop cat in a wheelchair who keeps you company while you work, and makes
you get up from the desk once an hour.

*Kočička* (roughly KOH-chich-kah) is Czech for "kitty". She speaks Czech for now; see [Language](#language).

One file. No dependencies beyond the Python standard library. No installer,
no account, no telemetry, nothing leaves your machine.

![Every pose she has, side by side](preview.png)

> 🇨🇿 Česká verze návodu je níž: [Česky](#česky)

---

## Why another desktop pet

Most desktop pets are decoration. This one actually looks after you:

- **She counts an hour of real work, not an hour on the clock.** If you walk
  away from the desk, she stops counting and goes to sleep. Your lunch break
  does not earn you a break, and neither does a laptop that was asleep.
- **She hides while you share your screen.** When an app goes fullscreen -
  a call, a slideshow, a video - she disappears until you come back.
- **Her breaks are guided.** Every hour she grows, holds up a STOP sign and
  counts down 30 seconds, walking you through a different stretch every few
  seconds while her body breathes in a 4-7-8 rhythm you can follow.
- **She asks what the one thing is today**, keeps it in her menu, and lets
  you tick it off.
- **She tracks your water** and gets pointed about it in the afternoon.
- **She tells you to stop working** once a day and then lies down.

And in between all that she rolls around, grooms a paw, meows, drinks milk,
eats grass, coughs up a hairball, climbs out of her cart for a nap, and
occasionally turns around and shows you her backside.

<p align="center"><img src="break.png" width="280" alt="The hourly break: she holds up a STOP sign with a 21 second countdown, the breathing phase and a stretch prompt, one paw held out"></p>

## About her cart

Rear-wheel carts are a real mobility aid for cats whose back legs do not carry
them, and cats get around in them happily. She is drawn the way those carts
actually work: her hind legs ride in a sling, a strap goes round her chest,
the wheels turn as she rolls, and when she wants a proper nap she climbs out
and lies down next to it. Nothing she says is about the cart, and none of her
jokes are at its expense. She is a cat with a cart, not a joke about one.

If you would rather have her on four legs, untick the cart in her menu.

## Running her

You need **Python 3** with tkinter, which the python.org and Microsoft Store
installers include. Nothing else.

```
python kocicka.py
```

On the first run she asks for a colour and a name, then remembers both in
`kocka.json` next to the script and comes back the same cat every time.

On Windows, double-click `kocicka.bat`; it starts her with `pythonw`, so no
console window stays open. To have her start with the machine, put a shortcut
to that `.bat` in `shell:startup`.

On Linux, some distributions ship tkinter separately (`sudo apt install
python3-tk` on Debian and Ubuntu).

## Controls

| | |
|---|---|
| **Left click** | she gives you a paw and says something |
| **Drag** | move her along the screen |
| **Right click** | today's one thing, come here, high five, milk, I drank, say something, take a break, cart on/off, rename / recolour, close |

## Platform support

She runs anywhere Python and tkinter do, but two of the good parts are
Windows-only and degrade quietly elsewhere:

| | Windows | macOS / Linux |
|---|---|---|
| Transparent background | yes | no, she sits on a small cream card |
| Knowing you left the desk | yes | assumes you are always there |
| Hiding on screen share | yes | no |
| Everything else | yes | yes |

The tests run on Windows, macOS and Linux in CI, but day to day she has only
been lived with on Windows. Under Wayland her borderless window may not stay
where she puts it. Patches for the macOS and Linux equivalents are very
welcome - see [CONTRIBUTING.md](CONTRIBUTING.md).

## Privacy

There is no networking code in `kocicka.py` at all: no `socket`, `urllib`,
`http` or `subprocess`, which you can check with a quick search. What she does
touch:

- **`kocka.json`** next to the script: her name and colour, the day you met,
  today's one thing, and today's water count. It is in `.gitignore`.
- **On Windows, two questions to the OS**, once a second: how long since the
  last key press or mouse move (`GetLastInputInfo`, a single timestamp, never
  which keys), and whether the window in front covers the whole screen
  (`GetForegroundWindow` and `GetWindowRect`, never its title or contents).

## Configuration

The constants at the top of `kocicka.py` are meant to be edited:

| | |
|---|---|
| `WORK_END = 16` | the hour she tells you to close the laptop |
| `PAUSE_EVERY = 3600` | seconds of real work between breaks |
| `PAUSE_SECS = 30` | how long a break lasts |
| `WATER_GOAL = 6` | glasses before she stops nagging |
| `AWAY_AFTER = 300` | seconds of no input before she assumes you left |
| `NIGHT = (22, 7)` | when she sleeps |
| `TASKBAR = 60` | raise this if she overlaps your taskbar |

## Language

Everything she says lives in the `LINES`, `MEOWS`, `HAIRBALL_SAYS`,
`BUTT_SAYS`, `BACK_SAYS`, `PAUSE_COACH` and `END_COACH` lists, and they are in
Czech, written to a woman (Czech grammar marks it). A few, to give you the
voice:

| | |
|---|---|
| *devět životů, dneska stačí zvládnout ten jeden* | nine lives, today you only need to get through this one |
| *pauza není lenost, je to strategie. zeptej se koček* | a break is not laziness, it is strategy. ask any cat |
| *ramena dozadu a dolů. celý den je držíš u uší* | shoulders back and down. you've had them by your ears all day |

An English set is the most useful contribution anyone could make.

## Checking it works

```
python kocicka.py --selftest              # her built-in check, no window
python -m unittest discover -s tests      # the test suite (drawing tests need a display)
python tools/pose.py                      # every pose side by side, to check the drawing
python tools/pose.py break                # the break sign, frozen mid-countdown
python kocicka.py --demo                  # speeds the timers up so you see a break now
```

CI runs the same on Windows, macOS and Linux, and also checks that `KOCICKA.md`
still matches the source.

---

## Česky

Kočička na vozíčku, která ti jezdí po spodku obrazovky, dělá ti společnost
při práci a jednou za hodinu tě zvedne od stolu.

Jeden soubor, jen standardní knihovna Pythonu. Nic neinstaluje, nic neposílá
na internet, nic o tobě nesbírá.

**Co potřebuješ:** Python 3. Najdeš ho v Microsoft Store (hledej „Python 3")
nebo na [python.org](https://www.python.org/downloads/) - tam při instalaci
zaškrtni „Add python.exe to PATH".

**Jak ji pustit:** dvojklik na `kocicka.bat`. Při prvním spuštění si vybereš
barvu a jméno, pak už naskakuje rovnou. Kdo nechce řešit GitHub, pošli mu
[`KOCICKA.md`](KOCICKA.md): je v něm celý návod i celý kód v jednom souboru.

**Co dělá:** projíždí se, olizuje se, mňouká, pije mlíčko, žere trávu a
vyblije chlupy, občas vyleze z vozíku a zdřímne si vedle něj. Každých pár
minut ti řekne něco povzbuzujícího. Jednou za hodinu **skutečné práce** tě
zastaví, zvedne ceduli STOP a vede tě protahováním a dýcháním 4-7-8.
Odpoledne ti řekne, ať to zavřeš. Pozná, když nejsi u počítače, a schová se,
když sdílíš obrazovku.

**Chceš přispět?** Viz [CONTRIBUTING.md](CONTRIBUTING.md). Nejvíc by teď
pomohly překlady hlášek a podpora macOS a Linuxu.

---

MIT, viz [LICENSE](LICENSE).

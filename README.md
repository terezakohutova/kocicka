# Kočička

A desktop cat in a wheelchair who keeps you company while you work, and makes
you get up from the desk once an hour.

One file. No dependencies beyond the Python standard library. No installer,
no account, no telemetry, nothing leaves your machine.

![Every pose she has, side by side](preview.png)

> 🇨🇿 Česká verze návodu je níž: [Česky](#česky)

---

## Why another desktop pet

Most desktop pets are decoration. This one actually looks after you:

- **She counts an hour of real work, not an hour on the clock.** If you walk
  away from the desk, she stops counting and goes to sleep. Your lunch break
  does not earn you a break.
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

## Running her

You need **Python 3**. Nothing else.

```
python kocicka.py
```

On the first run she asks for a colour and a name, then remembers both in
`kocka.json` next to the script and comes back the same cat every time.

On Windows you can save this as `kocicka.bat` and double-click it:

```bat
@echo off
start "" pythonw "%~dp0kocicka.py"
```

To have her start with the machine, put a shortcut to that `.bat` in
`shell:startup`.

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
| Transparent background | yes | no, she sits on a solid rectangle |
| Knowing you left the desk | yes | assumes you are always there |
| Hiding on screen share | yes | no |
| Everything else | yes | yes |

Patches for the macOS and Linux equivalents are very welcome - see
[CONTRIBUTING.md](CONTRIBUTING.md).

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

Everything she says lives in the `LINES`, `MEOWS` and `PAUSE_COACH` lists.
They are currently in Czech - translations are a great first contribution.

## Checking it works

```
python kocicka.py --selftest     # her logic, no window
python _pose.py                  # every pose side by side, to check the drawing
python kocicka.py --demo         # speeds the timers up so you see a break now
```

---

## Česky

Kočička na vozíčku, která ti jezdí po spodku obrazovky, dělá ti společnost
při práci a jednou za hodinu tě zvedne od stolu.

Jeden soubor, jen standardní knihovna Pythonu. Nic neinstaluje, nic neposílá
na internet, nic o tobě nesbírá.

**Co potřebuješ:** Python 3. Najdeš ho v Microsoft Store (hledej „Python 3")
nebo na [python.org](https://www.python.org/downloads/) - tam při instalaci
zaškrtni „Add python.exe to PATH".

**Jak ji pustit:** ulož vedle `kocicka.py` soubor `kocicka.bat` s obsahem
výše a dej na něj dvojklik. Při prvním spuštění si vybereš barvu a jméno,
pak už naskakuje rovnou.

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

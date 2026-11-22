#!/usr/bin/env python3
"""Kocicka - a desktop cat in a wheelchair who keeps you company and looks after you.

stdlib only (tkinter + ctypes), no install, nothing leaves your machine. Her new look is
pictures packed into this file (see SPRITES); the classic one is drawn in code.
On the first run she asks for a name and a colour; after that she remembers both in
her config file (see config_dir) and comes back the same cat. She notices when you step
away, gets out of the way of fullscreen apps, stops you for a stretch once an hour of
actual work, and calls it a day when the day is done.
  run:        python kocicka.py
  demo:       python kocicka.py --demo        (speeds the timers up so you see it now)
  self-check: python kocicka.py --selftest    (also runs tests/ when it sits next to her)
"""
from __future__ import annotations

import base64
import colorsys
import contextlib
import ctypes
import hashlib
import json
import math
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from datetime import date, datetime, timedelta
from pathlib import Path

W, H = 200, 230      # window size: cat in the bottom, speech bubble on top
GROUND = 210         # floor line inside the window
TASKBAR = 40         # bottom margin where the OS won't tell us its work area (macOS, Linux)
SPEED = 1.6          # px per frame while rolling
TICK = 40            # ms per frame while she rolls, coughs or holds the sign (twice that
                     # while she just sits and breathes)
TICK_SLEEP = 250     # ms per frame while she sleeps or naps: nothing moves fast then
TICK_HIDDEN = 500    # ms per frame while she is hidden: only the counting goes on
SLOW_EVERY = 1.0     # seconds between the expensive OS checks
IDLE_EVERY = 5.0     # macOS and Linux: seconds between asking the OS how long you've been idle
SAVE_WORK_EVERY = 60  # seconds between writing today's work time down, so a restart keeps it
LINE_EVERY = (180, 420)   # seconds between her little pep talks
PAUSE_EVERY = 3600        # seconds of ACTUAL work between the big stop-everything breaks
PAUSE_SECS = 30           # how long a break lasts
SNOOZE = 600              # "later" from the menu brings the break back this many seconds from now
END_SECS = 45             # how long the end-of-day wind-down lasts
END_AFTER_WORK = 1800     # no end-of-day sign until you've worked this long today
PAUSE_ZOOM = 2.0          # how much bigger she gets while holding the sign
PAUSE_EXTRA = 60          # headroom the window grows so the sign clears her ears
COACH_EVERY = 6           # seconds each stretch prompt stays up during the countdown
AWAY_AFTER = 300          # no keyboard or mouse for this long and she assumes you left;
                          # coming back after that counts as your break
WORK_END = 16             # hour she calls it a day and tells you to close the laptop
WATER_GOAL = 6            # glasses before she stops nagging
END_GRACE = 3600          # leave the desk within this long of the end-of-day sign = done on time
NIGHT = (22, 7)           # dozes from 22:00 to 07:00: no pep talks, no end-of-day sign, but
                          # your work still counts and night owls still get their break

PALETTES = {         # fur, shading/legs, nose
    "zrzava": ("#e8a75c", "#b9702e", "#f2a0a8"),
    "seda": ("#a8b2c1", "#6f7d91", "#e0a3ad"),
    "smetanova": ("#f0dfc2", "#c9ab82", "#f2a0a8"),
    "cerna": ("#55555f", "#33333a", "#e6909c"),
}
DEFAULT_FUR = "zrzava"
# wellness points unlock these for good: (what, points needed). Points are never taken away.
REWARDS = (("bow", 15), ("hat", 40), ("mata", 80), ("ruzova", 150))
WEARABLES = ("bow", "hat")
CART_COLOURS = {"fialova": None, "mata": 0.45, "ruzova": 0.93}   # hue; None = as drawn
DEFAULT_CART = "fialova"
LOOKS = ("new", "classic")
EYE, MOUTH = "#3b2b20", "#8a3a45"
KEY = "#ff00ff"      # transparent colour key (Windows only)

WHEEL_R = 20         # rear-wheel cart for a cat whose back legs don't carry her
FRAME, TIRE, RIM, STRAP = "#9aa0a8", "#3f3f46", "#c9ccd1", "#d2533f"
BOWL, MILK, GRASS, STAR = "#cfd6de", "#fdfdfb", "#7ba05b", "#d97757"
PAPER, INK, MUTED = "#faf7f2", "#2b2b2b", "#6b6b6b"
FONT = "Segoe UI"

# Every word she shows you, in one place. Czech only for now, and she talks to a woman
# (Czech grammar marks it: "napila jsem se", "ty bys neměla"). A translation is a second
# table of this same shape; please write it in her voice rather than translating word
# for word.
STRINGS = {
    # encouraging, funny, and always from a cat's point of view
    "lines": [
        "devět životů, dneska stačí zvládnout ten jeden",
        "i kočka spadne. jen pak tváří, že to bylo schválně",
        "protáhni se. děláme to 40× denně a koukni, jak vypadáme",
        "kdybys byla kočka, tohle už dávno shodíš ze stolu",
        "nikdo nemá všechno pod kontrolou. my to jen líp hrajeme",
        "mrrr. to znamená, že ti fandím",
        "dýchej zhluboka. příst se jinak nedá",
        "dneska stačí být o chlup lepší. doslova o chlup",
        "když nevíš kudy dál, sedni si do krabice. mně to pomáhá",
        "napij se. já vodu z misky taky ignoruju, ale ty bys neměla",
        "koukat z okna je taky práce. dělám ji šest hodin denně",
        "rozbilo se to? nic se neděje. já to dělám schválně",
        "tvůj seznam úkolů není tvých devět životů",
        "postav se a protáhni. shodím ti za to něco ze stolu",
        "jdeš správným směrem, jen pomaleji než myš. to nevadí",
        "i nejlepší lovec občas mine. pak dělá, že nelovil",
        "dej si pauzu, klávesnici ti tu pohlídám",
        "tohle zvládneš. věř kočce, my ty věci cítíme dopředu",
        "nemusíš příst pořád. někdy stačí jen ležet",
        "pauza není lenost, je to strategie. zeptej se koček",
        "tvoje židle je teď moje. ber to jako pozvánku vstát",
        "hlavu vzhůru, uši dozadu, jdeme na to",
        "kdyby to bylo lehké, neměla bys radost. ani já z krabice",
        "zamrkej. já to dělám pomalu a znamená to, že tě mám ráda",
        "spadlo to ze stolu? tak tam nemělo co dělat",
        "dneska jsi toho zvládla dost. věř mi, já tu byla celou dobu",
        "když se ti nechce, lehni si na to. já to řeším vždycky takhle",
        "nemusíš se líbit všem. já se líbím, jen když mám hlad",
        "zavři pět záložek. i já mám v hlavě jen jednu myš",
        "když ti to nejde, zkus to z druhé strany. nebo shora",
        "první pokus nevyšel? proto máme těch devět životů",
        "slunce na klávesnici znamená pauzu. to je zákon",
        "nejlepší nápady mám ve tři ráno. tobě je radši neřeknu",
        "nemusíš běhat. kočky chodí a stejně jsou všude dřív",
        "spočítej do deseti a pak to pošli. nebo to shoď ze stolu",
        "ty maily ti neutečou. hlídám je, jsou pomalé jako želvy",
        "chce to sednout a začít. já si sedám klidně půl hodiny",
        "když se bojíš, nafoukni se. mně to na psy funguje",
        "dneska nemusíš být velká kočka. stačí být kočka",
        "tvoje hodnota není v počtu odškrtnutých políček",
        "kdo pořád kouká na hodiny, nikdy nechytí myš",
        "máš hlad? jdi se najíst. já bych ti to řekla už dávno",
        "čaj vystydl. to je znamení, že u toho sedíš moc dlouho",
        "koukáním se to nespraví. leda já, na mě koukej dál",
        "když je toho moc, dělej jednu věc. já dělám tuhle: spím",
        "tvoje ráno začíná, až se protáhneš. ani o chvíli dřív",
        "nechala sis to na později? později je taky dneska",
        "buď na sebe hodná. jsi jediná, kterou máš",
        "jsi rychlejší, než si myslíš. jenom šetříš energii",
        "shodila jsem to já. ale mohl to být i průvan",
        "když nevíš, co říct, mlč a koukej. mně to vždycky projde",
        "tvoje hlava není stroj. je to kočka. potřebuje spát",
        "ta práce tu byla před tebou a bude tu i po tobě",
        "nedělej deset věcí naráz. ani já nemám deset tlapek",
        "když tě někdo štve, otoč se k němu zády. naučím tě to",
        "pochval se nahlas. já si předu i sama pro sebe",
        "nejde to? nech to uležet. ráno je moudřejší než večer",
        "úkol, kterého se bojíš, bývá tak na deset minut",
        "dej si teplý čaj a chvíli nic. v tom je celé kouzlo",
        "nemusíš odpovídat hned. já se ozvu, až budu mít hlad",
        "srovnávat se s ostatními je jak honit vlastní ocas",
        "dneska stačí přežít. zítra jdeme zase lovit",
        "nikdo tě nehlídá. teda kromě mě, ale já držím basu",
        "je ti zima? přitáhni si deku. ta práce počká v teple",
        "strach z chyby bývá větší než ta chyba. věř kočce",
        "polož ten telefon. není v něm nic, co bych nevěděla",
        "nádech na čtyři, zadrž na sedm, výdech na osm. předu s tebou",
        "nemusíš mít hotovo. dneska stačí mít začato",
        "pochybnosti nech spát. zrovna na nich ležím",
        "zavolej jí. já bych na ni aspoň mňoukla",
        "napsat to blbě je pořád lepší než nenapsat nic",
        "až budeš unavená, přijď si lehnout. udělám ti místo",
        "zamkni ten mail a jdi na vzduch. já hlídám okno",
        "co je rozdělané, není pokažené. jen to čeká",
        "všechno nestihneš. ani já neolíznu celou tlapku naráz",
        "dneska jsi udělala víc, než si pamatuješ. já to počítám",
    ],
    "meows": ["mňau", "mrrrp", "mňaaau", "prrr", "mrr?"],
    "hairball": ["hrk... hrk...", "ehm. moment", "nekoukej na mě"],
    "butt": ["tohle je pro tebe", "*ocas nahoru*", "koukej", "tak co"],
    "back": ["a jsi zpátky", "kde jsi byla?", "hlídala jsem ti to", "*protahuje se*"],
    # what she coaches you through while the countdown runs
    "pause_coach": [
        "postav se a protáhni se. jako kočka po spaní",
        "ruce nad hlavu, záda do oblouku. drž to a dýchej",
        "otoč hlavu doleva a doprava. pomalu, nikam nespěcháme",
        "ramena dozadu a dolů. celý den je držíš u uší",
        "koukni se z okna na něco daleko. oči si odpočinou",
        "protáhni krk. celý den koukáš dolů jako na myš",
        "postav se na špičky a natáhni se ke stropu",
        "zatoč rameny dozadu. pětkrát. počítám s tebou",
        "sedni si rovně a zhluboka se nadechni. třikrát",
        "protřep ruce a zápěstí. píšeš od rána",
    ],
    "end_coach": [
        "zavři to. zítra to tam bude pořád",
        "co nestihneš dneska, uteče pomalu jako stará myš",
        "šichta končí. jdi si lehnout do krabice",
        "hotovo je líp než dokonalé. ptej se koček",
        "postav se. dneska už na tu židli nesedej",
        "protáhni se naposled a jdi pryč od stolu",
        "dobrá práce. teď ji nech být",
    ],
    "breath": ("nádech", "zadrž", "výdech"),       # 4-7-8: in, hold, out
    # the signs
    "sign_break": ("STOP", "teď pauzička"),
    "sign_end": ("ŠICHTA KONČÍ", "hotovo. zavři to"),
    "sign_count": "%d s  ·  %s",
    # her memory and the day
    "fallback_name": "Kočička",
    "hello": "ahoj, jsem %s",
    "missed_you": "chyběla jsi mi! %s jsme se neviděly",
    "day_n": "zase já. jsme spolu %d. den",
    "days": ("den", "dny", "dní"),                 # 1, 2-4, 5+
    "minutes": ("minutu", "minuty", "minut"),      # "za" 1, 2-4, 5+
    "water_none": "dneska ses ještě nenapila. ani jednou. koukám",
    "water_some": "dneska jsme to daly %d×. na kočku dobrý, na člověka málo",
    "water_count": "%d. dneska. ještě %d",
    "water_done": "%d. a to je ono",
    "focus_none": "dnes: (nic)",
    "focus_today": "dnes: ",
    "focus_done": "hotovo: ",
    "focus_proud": "jsem na tebe pyšná",
    "focus_undo": "tak jo, jedem dál",
    "focus_title": "Jedna věc",
    "focus_ask": "Co je dneska ta jedna věc, kterou chceš mít hotovou?",
    "focus_ok": "jdu na to",
    "renamed": "teď jsem %s",
    "skipped": "dobře, tentokrát ne. ale příště jo",
    "snoozed": "tak za %s. budu to hlídat",          # %s: SNOOZE in minutes
    "cant_save": "nemůžu si nic zapamatovat, nejde mi zapisovat do složky",
    # the welcome window
    "welcome_title": "Vítej!",
    "welcome_head": "Máš novou kočku.",
    "welcome_sub": "Vyber jí barvu a dej jí jméno.",
    "welcome_name": "Jak se bude jmenovat?",
    "welcome_go": "Pojď ke mně!",
    "fur_labels": (("zrzava", "zrzavá"), ("seda", "šedá"),
                   ("smetanova", "smetanová"), ("cerna", "černá")),
    # the right-click menu
    "menu_come": "pojď sem",
    "menu_paw": "dej packu",
    "menu_milk": "mlíčko",
    "menu_drank": "napila jsem se",
    "menu_say": "řekni něco",
    "menu_break": "dáme pauzu",
    "menu_skip": "přeskočit pauzu",
    "menu_snooze": "pauzu až za %s",
    "menu_cart": "vozíček",
    "menu_rename": "přejmenovat / barva",
    "menu_close": "zavřít",
    "menu_look": "vzhled",
    "look_new": "nový",
    "look_classic": "klasický",
    # wellness points: one for each real thing, never taken away, never a reproach
    "menu_points": "wellness body",
    "points": ("bod", "body", "bodů"),             # 1, 2-4, 5+
    "points_total": "celkem %s, série %s",
    "points_how": "za pauzu, vodu, jednu věc a konec včas",
    "week_join": " · ",
    "weekdays": ("po", "út", "st", "čt", "pá", "so", "ne"),
    "reward_labels": {"bow": "mašlička", "hat": "čepička", "fialova": "fialový vozíček",
                      "mata": "mátový vozíček", "ruzova": "růžový vozíček"},
    "reward_won": {"bow": "mašličku", "hat": "čepičku", "mata": "mátový vozíček",
                   "ruzova": "růžový vozíček"},
    "locked": "%s (od %d bodů)",
    "unlocked": "odemkla sis %s! najdeš to v menu",
    "new_look_only": "doplňky jsou vidět v novém vzhledu",
}

# what she gets up to on her own, and how long each one lasts
TRICKS = ("walk", "walk", "walk", "idle", "lick", "meow", "milk", "grass",
          "rest", "highfive", "hairball", "butt", "sit")
DURATION = {"rest": (9, 18), "milk": (5, 9), "grass": (5, 9), "hairball": (4.5, 6.5),
            "lick": (3, 5), "meow": (1.5, 2.5), "butt": (3, 5)}


# --------------------------------------------------------------------------- Windows sensing

class _LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", _RECT), ("rcWork", _RECT),
                ("dwFlags", ctypes.c_ulong)]


_LII = _LASTINPUTINFO()
_LII.cbSize = ctypes.sizeof(_LII)
_DESKTOP_CLASSES = ("Progman", "WorkerW")   # the desktop itself: fullscreen, but not an app


def _load_win32():
    try:
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    except AttributeError:
        return None, None                      # not Windows
    # declared up front, so 64-bit window handles are never squeezed through a C int
    hwnd = ctypes.c_void_p
    for name in ("GetForegroundWindow", "GetShellWindow", "GetDesktopWindow"):
        getattr(user32, name).restype = hwnd
    user32.GetWindowLongW.argtypes = (hwnd, ctypes.c_int)
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.GetWindowRect.argtypes = (hwnd, ctypes.POINTER(_RECT))
    user32.GetClassNameW.argtypes = (hwnd, ctypes.c_wchar_p, ctypes.c_int)
    user32.MonitorFromWindow.argtypes = (hwnd, ctypes.c_uint32)
    user32.MonitorFromWindow.restype = ctypes.c_void_p
    user32.GetMonitorInfoW.argtypes = (ctypes.c_void_p, ctypes.POINTER(_MONITORINFO))
    user32.SystemParametersInfoW.argtypes = (ctypes.c_uint, ctypes.c_uint,
                                             ctypes.POINTER(_RECT), ctypes.c_uint)
    kernel32.GetTickCount.restype = ctypes.c_uint32
    return user32, kernel32


_USER32, _KERNEL32 = _load_win32()


def _win32():
    """user32 and kernel32 on Windows, (None, None) everywhere else."""
    return _USER32, _KERNEL32


def _box(r: _RECT) -> tuple:
    return (r.left, r.top, r.right, r.bottom)


_IDLE_CACHE = {"at": -1e18, "value": 0.0}


def _ask_idle(platform: str, run, which) -> float:
    """macOS: ioreg's HIDIdleTime (nanoseconds). Linux: xprintidle (milliseconds), which
    only answers under X11 and only if it is installed. 0 for anything else."""
    if platform == "darwin":
        cmd, pattern, unit = ["ioreg", "-c", "IOHIDSystem"], r'"HIDIdleTime" = (\d+)', 1e9
    elif platform.startswith("linux") and which("xprintidle"):
        cmd, pattern, unit = ["xprintidle"], r"^\s*(\d+)\s*$", 1e3
    else:
        return 0.0
    try:
        done = run(cmd, capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return 0.0
    found = re.search(pattern, done.stdout or "") if done.returncode == 0 else None
    return int(found.group(1)) / unit if found else 0.0


def idle_seconds(platform: str = sys.platform, run=None, which=shutil.which,
                 clock=time.monotonic) -> float:
    """Seconds since you last touched the keyboard or mouse. 0 where we can't tell, which
    means she assumes you are there: Wayland, or Linux without xprintidle."""
    if platform.startswith("win"):
        user32, kernel32 = _win32()
        if not user32 or not user32.GetLastInputInfo(ctypes.byref(_LII)):
            return 0.0
        # GetTickCount wraps every 49 days, so subtract inside 32 bits or she thinks you left
        return ((kernel32.GetTickCount() - _LII.dwTime) % (2 ** 32)) / 1000.0
    now = clock()                              # elsewhere it costs a little program, so
    if now - _IDLE_CACHE["at"] >= IDLE_EVERY:  # she asks every few seconds, not every one
        _IDLE_CACHE.update(at=now, value=_ask_idle(platform, run or subprocess.run, which))
    return _IDLE_CACHE["value"]


def covers(window: tuple, monitor: tuple) -> bool:
    """True when the window rectangle reaches every edge of the monitor rectangle."""
    return (window[0] <= monitor[0] and window[1] <= monitor[1]
            and window[2] >= monitor[2] and window[3] >= monitor[3])


def fullscreen_in_front() -> bool:
    """True when the window in front fills its whole monitor without a title bar: a
    slideshow, a fullscreen call or video, a game. That is all it can tell. It can't see
    whether you are sharing your screen, so a shared window that isn't fullscreen does
    not hide her. Asks only for the window's style, size and class, never its title."""
    user32, _ = _win32()
    if not user32:
        return False
    hwnd = user32.GetForegroundWindow()
    if not hwnd or hwnd in (user32.GetShellWindow(), user32.GetDesktopWindow()):
        return False
    if user32.GetWindowLongW(hwnd, -16) & 0x00C00000:   # GWL_STYLE & WS_CAPTION
        return False       # it still has a title bar, so it's only maximised, not fullscreen
    name = ctypes.create_unicode_buffer(32)
    user32.GetClassNameW(hwnd, name, 32)
    if name.value in _DESKTOP_CLASSES:
        return False       # you clicked the wallpaper; that isn't a presentation
    rect = _RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False
    monitor = user32.MonitorFromWindow(hwnd, 2)          # MONITOR_DEFAULTTONEAREST
    info = _MONITORINFO()
    info.cbSize = ctypes.sizeof(_MONITORINFO)
    if not monitor or not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return False
    return covers(_box(rect), _box(info.rcMonitor))


def work_area(screen_w: int, screen_h: int) -> tuple:
    """(left, top, right, bottom) of the primary screen minus the taskbar, wherever it is
    docked. Windows says exactly; elsewhere we guess TASKBAR pixels off the bottom."""
    user32, _ = _win32()
    if user32:
        r = _RECT()
        got = user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)   # SPI_GETWORKAREA
        if got and r.right > r.left and r.bottom > r.top:
            return _box(r)
    return (0, 0, screen_w, max(H, screen_h - TASKBAR))


def set_dpi_awareness() -> str:
    """Tell Windows we draw at real pixels, so she is crisp instead of blurry-stretched.
    Must run before the first Tk window. Returns what it managed, for the curious."""
    try:
        windll = ctypes.windll
    except AttributeError:
        return "not windows"
    with contextlib.suppress(AttributeError, OSError):
        if windll.shcore.SetProcessDpiAwareness(2) == 0:     # per-monitor (8.1+), S_OK
            return "per-monitor"
    with contextlib.suppress(AttributeError, OSError):
        if windll.user32.SetProcessDPIAware():               # system-wide (Vista+), BOOL
            return "system"
    return "none"


# --------------------------------------------------------------------------- behaviour

class Pet:
    """Position + behaviour. No tkinter in here, so it can be tested headless.

    Positions are in her own units (one unit is one pixel at 100 % display scaling).
    """

    def __init__(self, screen_w: float, x: float | None = None):
        self.screen_w = screen_w
        self.x = screen_w // 2 if x is None else x
        self.dir = 1
        self.state = "idle"
        self.until = 0.0
        self.say = ""
        self.say_until = 0.0
        self.extra = []      # lines the app wants her to say today, on top of the usual
        self.next_line = time.time() + random.uniform(*LINE_EVERY)
        self.worked = 0.0    # seconds of real work since her last break
        self.total = 0.0     # seconds of real work since she started, never reset
        self.away_since = 0.0  # when she noticed you had gone, 0 while you are here
        self.due_at = 0.0    # a snoozed break comes back at this time on the clock, 0 = none
        self.last_step = 0.0
        self.kind = "break"  # which sign the current pause is showing
        self.pause_until = 0.0
        self.pause_span = float(PAUSE_SECS)
        self.coach = []      # the prompts she walks you through during a break
        self.breath, self.breath_word = 0.0, ""
        self.started = 0.0   # when the current state began
        self.progress = 0.0  # 0 -> 1 through the current state, for timed animations
        self.cart = True     # rear-wheel cart: rear legs ride in slings, wheels carry her
        self.roll = 0.0      # distance rolled, drives the spoke rotation
        self.fur = DEFAULT_FUR
        self.look = "classic"   # "new" = the pictures, "classic" = drawn in code
        self.wear = ()          # what she has on, new look only: "bow", "hat"
        self.cart_colour = DEFAULT_CART
        self.completed = ""     # the kind of sign she just held to the very end, once
        self.heart_until = 0.0  # a little heart over her head after a wellness point

    @property
    def max_x(self) -> float:
        return max(0, self.screen_w - W)

    @property
    def colours(self) -> tuple:
        """(fur, shading, nose) for her coat."""
        return PALETTES.get(self.fur, PALETTES[DEFAULT_FUR])

    def asleep(self, hour: int) -> bool:
        return hour >= NIGHT[0] or hour < NIGHT[1]

    def speak(self, text: str, now: float, secs: float = 4) -> None:
        self.say, self.say_until = text, now + secs

    def chatter(self, now: float) -> None:
        self.speak(random.choice(STRINGS["lines"] + self.extra), now, 7)

    def do(self, state: str, now: float, secs: float | None = None) -> None:
        """Switch to a state for secs seconds, or for its usual random length if None."""
        self.state = state
        self.started = now
        if secs is None:
            secs = random.uniform(*DURATION.get(state, (2.5, 6)))
        self.until = now + secs

    def start_pause(self, now: float, kind: str = "break") -> None:
        span = PAUSE_SECS if kind == "break" else END_SECS
        prompts = STRINGS["pause_coach" if kind == "break" else "end_coach"]
        self.state, self.dir, self.say, self.kind = "pause", 1, "", kind
        self.pause_until, self.pause_span = now + span, float(span)
        self.worked, self.due_at = 0.0, 0.0
        self.coach = random.sample(prompts, k=min(len(prompts), max(1, span // COACH_EVERY)))

    def finish_pause(self, now: float, lie_down: bool = True) -> None:
        """Put the sign down: on time, or early when you dismiss or skip it."""
        self.breath, self.pause_until = 0.0, min(self.pause_until, now)
        if self.kind == "end" and lie_down:
            self.do("rest", now, 90)           # shift's over, she lies down with you
        else:
            self.state, self.until = "idle", 0.0

    def pause_left(self, now: float) -> int:
        return max(0, math.ceil(self.pause_until - now))

    def coach_line(self, now: float) -> str:
        """The stretch she's asking for right now; a new one every COACH_EVERY seconds."""
        if not self.coach:
            return ""
        done = self.pause_span - max(0.0, self.pause_until - now)
        return self.coach[min(len(self.coach) - 1, int(done // COACH_EVERY))]

    def zoom(self, now: float) -> float:
        """1.0 normally; eases up to PAUSE_ZOOM for a break and back down at the end."""
        if self.state != "pause":
            return 1.0
        left = max(0.0, self.pause_until - now)
        eased = min(1.0, (self.pause_span - left) / 0.5, left / 0.5)
        return 1.0 + (PAUSE_ZOOM - 1.0) * eased

    def _breathe(self, now: float) -> None:
        """4-7-8: her whole body does it so you can follow the cat instead of the text."""
        inhale, hold, exhale = STRINGS["breath"]
        cycle = (now - (self.pause_until - self.pause_span)) % 19.0
        if cycle < 4:
            self.breath, self.breath_word = cycle / 4.0, inhale
        elif cycle < 11:
            self.breath, self.breath_word = 1.0, hold
        else:
            self.breath, self.breath_word = 1.0 - (cycle - 11) / 8.0, exhale

    def break_due(self, now: float) -> bool:
        """An hour of work is full, or a snoozed break's ten minutes on the clock are up."""
        if self.due_at:
            return now >= self.due_at
        return self.worked >= PAUSE_EVERY

    def step(self, now: float, hour: int, away: bool = False, hidden: bool = False) -> str:
        """Advance her by one frame. While hidden (a fullscreen app is in front) your work
        still counts, but she keeps quiet and a due break waits until she is back. Time
        away from the desk is a break of its own. At night she dozes, but your work
        still counts and a break still comes."""
        dt = min(2.0, max(0.0, now - self.last_step)) if self.last_step else 0.0
        self.last_step = now
        if self.say and now > self.say_until:
            self.say = ""

        if self.state == "pause":
            self._breathe(now)
            if now >= self.pause_until:
                self.completed = self.kind     # sat through all of it: that earns a point
                self.finish_pause(now)
            return self.state

        night = self.asleep(hour)
        if away:
            self.state = "away"                # nobody to talk to, so she naps instead
            self.away_since = self.away_since or now
            self.next_line = now + random.uniform(*LINE_EVERY)
            return self.state
        if self.state == "away":
            # you were gone AWAY_AFTER before she noticed, plus however long since
            if now - (self.away_since or now) + AWAY_AFTER >= PAUSE_SECS:
                self.worked, self.due_at = 0.0, 0.0    # that was your break
            self.state, self.until = "idle", 0.0
            if not night:
                self.do("idle", now, 3)        # a beat to notice you, before anything else
                self.speak(random.choice(STRINGS["back"]), now, 5)
        self.away_since = 0.0

        self.worked += dt                      # only counts while you are actually here
        self.total += dt
        if hidden:                             # nobody can see her: count, but say nothing
            self.next_line = max(self.next_line, now + 5)
            return self.state
        if self.break_due(now):
            self.start_pause(now)
            return self.state
        if night:
            self.state = "sleep"
            # keep sliding the timer, or she'd blurt a pep talk the second she wakes up
            self.next_line = now + random.uniform(*LINE_EVERY)
            return self.state
        if self.state == "sleep":
            self.state, self.until = "idle", 0.0
        if now >= self.next_line:
            self.chatter(now)
            self.next_line = now + random.uniform(*LINE_EVERY)
        if now >= self.until:
            if self.state == "grass" and random.random() < 0.7:
                self.do("hairball", now)       # grass goes down, fur comes up. that's the deal
            else:
                # in the cart the wheels hold her rear up, so sitting is off the menu
                self.do(random.choice([s for s in TRICKS if not (self.cart and s == "sit")]), now)
            if self.state == "walk":
                self.dir = random.choice((-1, 1))
            elif self.state == "meow":
                self.speak(random.choice(STRINGS["meows"]), now, 2.5)
            elif self.state == "hairball":
                self.speak(random.choice(STRINGS["hairball"]), now, 3)
            elif self.state == "butt":
                self.speak(random.choice(STRINGS["butt"]), now, 3)
        span = max(0.001, self.until - self.started)
        self.progress = min(1.0, max(0.0, (now - self.started) / span))
        if self.state == "walk":
            self.x += self.dir * SPEED
            self.roll += SPEED
            if not 0 <= self.x <= self.max_x:
                self.dir *= -1
                self.x = min(self.max_x, max(0, self.x))
        return self.state


# --------------------------------------------------------------------------- drawing

def bowl_box(direction: int) -> tuple:
    """Where her milk bowl sits (x1, y1, x2, y2), in unzoomed window units. She puts it
    under her nose, so it swaps sides when she faces left."""
    x1, x2 = 130, 176
    if direction < 0:
        x1, x2 = W - x2, W - x1
    return (x1, GROUND - 18, x2, GROUND - 2)


def starburst(c, cx, cy, r, angle, rays=11, colour=STAR):
    """A spinning many-pointed star. Also, apparently, what a cat shows you."""
    c.create_oval(cx - r * 0.15, cy - r * 0.15, cx + r * 0.15, cy + r * 0.15,
                  fill=colour, outline="")
    for i in range(rays):
        a = angle + i * 2 * math.pi / rays
        c.create_polygon(                      # a tapered petal: tip, shoulder, waist, shoulder
            cx + math.cos(a) * r, cy + math.sin(a) * r,
            cx + math.cos(a - 0.30) * r * 0.30, cy + math.sin(a - 0.30) * r * 0.30,
            cx + math.cos(a) * r * 0.10, cy + math.sin(a) * r * 0.10,
            cx + math.cos(a + 0.30) * r * 0.30, cy + math.sin(a + 0.30) * r * 0.30,
            fill=colour, outline="")


def draw_bubble(c, pet, hy, k=1.0):
    """Sized to the wrapped text and anchored above her head, never mirrored. Drawn after
    the zoom, at final size, so the text and its box always match."""
    if not pet.say:
        return
    dark = pet.colours[1]
    mid = W // 2 * k
    said = c.create_text(mid, (hy - 42) * k, text=pet.say, width=(W - 30) * k, anchor="s",
                         justify="center", fill=INK, font=(FONT, -round(12 * k), "bold"),
                         tags=("bubble",))
    x1, y1, x2, y2 = c.bbox(said)
    for dx, dy, r in ((16, 10, 5), (26, 20, 3)):
        c.create_oval(mid + dx * k, y2 + dy * k, mid + (dx + r * 2) * k, y2 + (dy + r * 2) * k,
                      fill="white", outline=dark, width=2 * k, tags=("bubble",))
    box = c.create_rectangle(x1 - 10 * k, y1 - 7 * k, x2 + 10 * k, y2 + 7 * k,
                             fill="white", outline=dark, width=2 * k, tags=("bubble",))
    c.tag_lower(box, said)


def draw_rear(c, pet, frame):
    """She turns her back on you. What you get is a spinning star where her tail starts."""
    fur, dark, _ = pet.colours
    cx, ay = W // 2, GROUND - WHEEL_R
    top, bottom = GROUND - 96, GROUND - 14

    if pet.cart:
        for wx in (cx - 54, cx + 54):
            c.create_oval(wx - WHEEL_R, ay - WHEEL_R, wx + WHEEL_R, ay + WHEEL_R,
                          fill=TIRE, outline="", tags=("wheel",))
            c.create_oval(wx - WHEEL_R + 5, ay - WHEEL_R + 5,
                          wx + WHEEL_R - 5, ay + WHEEL_R - 5, fill=RIM, outline="")
            for k in range(3):
                a = pet.roll / WHEEL_R + k * math.pi / 3
                dx, dy = math.cos(a) * (WHEEL_R - 6), math.sin(a) * (WHEEL_R - 6)
                c.create_line(wx - dx, ay - dy, wx + dx, ay + dy, width=2, fill=FRAME)
            c.create_oval(wx - 4, ay - 4, wx + 4, ay + 4, fill=FRAME, outline="")
        c.create_line(cx - 54, ay, cx - 38, top + 16, cx + 38, top + 16, cx + 54, ay,
                      width=5, fill=FRAME, capstyle="round", joinstyle="round", smooth=True)

    for lx in (cx - 30, cx + 30):              # hind paws poking out below the rump
        c.create_line(lx, bottom - 12, lx, GROUND, width=10, fill=dark, capstyle="round")

    sway = math.sin(frame * 0.11) * 9          # tail straight up, the way they do it
    c.create_line(cx + 2, top + 26, cx + 8 + sway * 0.4, top - 14,
                  cx + 10 + sway, top - 44,
                  width=9, fill=fur, capstyle="round", smooth=True)

    c.create_oval(cx - 26, top - 30, cx + 26, top + 18, fill=fur, outline="")   # back of head
    for ex, tilt in ((cx - 17, -9), (cx + 17, 9)):
        c.create_polygon(ex - 9, top - 20, ex + tilt, top - 44, ex + 9, top - 18,
                         fill=fur, outline="")
    c.create_oval(cx - 44, top, cx + 44, bottom, fill=fur, outline="")          # the rump
    for sx in (-22, 0, 22):                                                     # stripes
        c.create_line(cx + sx, top + 10, cx + sx, top + 30, width=4, fill=dark, capstyle="round")

    # a pale patch so the star reads on any coat, then the star
    cy = (top + bottom) / 2 + 12
    c.create_oval(cx - 26, cy - 26, cx + 26, cy + 26, fill="#fdf6ec", outline="")
    starburst(c, cx, cy, 22, frame * 0.05)


def draw(c, pet, frame, k=1.0):
    """Draw her k times her normal size (display scaling times the break zoom)."""
    if pet.look == "new":
        draw_cute(c, pet, frame, k)
        return
    c.delete("all")
    st = pet.state
    fur, dark, pink = pet.colours
    if st == "butt":
        draw_rear(c, pet, frame)
        zoom_canvas(c, k)
        draw_bubble(c, pet, GROUND - 120, k)
        return

    f = 1 if pet.dir >= 0 else -1
    fx = (lambda x: x) if f > 0 else (lambda x: W - x)

    def oval(x1, y1, x2, y2, **kw):
        a, b = fx(x1), fx(x2)
        c.create_oval(min(a, b), y1, max(a, b), y2, **kw)

    def line(pts, **kw):
        c.create_line([v for x, y in pts for v in (fx(x), y)], **kw)

    def poly(pts, **kw):
        c.create_polygon([v for x, y in pts for v in (fx(x), y)], **kw)

    t = frame * 0.12
    sleeping = st in ("sleep", "away")
    resting = st == "rest"                     # she climbs out and lies down next to the cart
    napping = sleeping or resting              # eyes shut either way
    in_cart = pet.cart and not resting
    lie = resting or (sleeping and not pet.cart)
    sit = st in ("sit", "highfive", "pause")
    by = GROUND - (20 if lie else 50 if in_cart else 40 if sit else 46)   # body centre
    by += 0 if lie else math.sin(t) * 1.5                                 # breathing
    puff = pet.breath * 5 if st == "pause" else 0    # the 4-7-8 breath, visible
    cby = GROUND - 50                          # the cart stands where it stands, empty or not
    bx = 22 if resting else 0                  # she lies down beside her cart, not inside it
    head_down = st in ("milk", "grass")        # nose to the floor
    heave = math.sin(t * 3.2) * 5 if st == "hairball" else 0
    hx = 138 + bx + (10 + heave if st == "hairball" else 0)
    hy = by - (4 if lie else 14 if sleeping else -8 if head_down else 2 if st == "hairball"
               else 26)
    ax, ay = 42, GROUND - WHEEL_R              # cart axle, behind her

    # tail (lifted clear of the cart frame when she's in it)
    sway = math.sin(t * (0.6 if lie else 1.4)) * (4 if lie else 11)
    line([(58, by + 6), (36, by - 14 + sway), (34, by - 44 + sway)] if in_cart else
         [(58 + bx, by + 6), (34 + bx, by - 4 + sway), (28 + bx, by - 26 + sway)],
         width=9, fill=fur, capstyle="round", smooth=True)

    # wheels, drawn behind the body so the haunch overlaps their inner edge
    if pet.cart:
        for cx, cy, r, tire in ((ax + 13, ay - 9, WHEEL_R - 4, "#2b2b30"),   # far wheel
                                (ax, ay, WHEEL_R, TIRE)):                    # near wheel
            oval(cx - r, cy - r, cx + r, cy + r, fill=tire, outline="", tags=("wheel",))
            oval(cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5, fill=RIM, outline="")
            for i in range(3):
                a = pet.roll / WHEEL_R + i * math.pi / 3
                dx, dy = math.cos(a) * (r - 6), math.sin(a) * (r - 6)
                line([(cx - dx, cy - dy), (cx + dx, cy + dy)], width=2, fill=FRAME)
            oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=FRAME, outline="")
        line([(50, ay - 4), (82, ay - 12)], width=5, fill=STRAP, capstyle="round")  # sling

    # bowl of milk, set down right under her nose
    if st == "milk":
        x1, y1, x2, y2 = bowl_box(1)           # oval() mirrors it when she faces left
        oval(x1, y1, x2, y2, fill=BOWL, outline=FRAME, width=2, tags=("bowl",))
        oval(x1 + 5, y1 + 2, x2 - 5, y2 - 6, fill=MILK, outline="", tags=("bowl",))

    # a tuft of grass to chew on, and the hairball it leads to
    if st == "grass":
        for gx, gh, bend in ((132, 30, 7), (141, 42, -6), (150, 36, 9), (159, 26, -5)):
            line([(gx, GROUND - 2), (gx + bend, GROUND - gh)],
                 width=4, fill=GRASS, capstyle="round", smooth=True, tags=("grass",))
    elif st == "hairball" and pet.progress > 0.6:
        oval(158, GROUND - 13, 186, GROUND - 2, fill=dark, outline="", tags=("hairball",))
        oval(163, GROUND - 14, 179, GROUND - 6, fill=fur, outline="", tags=("hairball",))

    # legs (front pair sits wide apart so they don't collapse into one stub)
    if not lie:
        sw = math.sin(t * 2.2) * 7 if st == "walk" else 0
        for i, (lx, ph) in enumerate(((76, 1), (88, -1), (110, -1), (128, 1))):
            if i < 2:                                           # rear pair
                if in_cart:                                     # slung, never reaches the floor
                    line([(lx - 4, by + 12), (lx - 20, ay - 2)],
                         width=9, fill=dark, capstyle="round", tags=("leg",))
                    continue
                if sit:
                    continue                                    # folded under when sitting
            if i == 3 and st in ("lick", "highfive", "pause"):
                continue                                        # raised paw, drawn over the body
            tipx, tipy = lx + (sw * ph if st == "walk" else 0), GROUND
            line([(lx, by + 14), (tipx, tipy)], width=10, fill=dark, capstyle="round",
                 tags=("leg",))

    # body + stripes
    oval(55 + bx - puff, by - 24 - puff, 136 + bx + puff, by + 22 + puff, fill=fur, outline="",
         tags=("body",))
    for sx in (80, 96, 112):
        line([(sx + bx, by - 21), (sx - 7 + bx, by - 4)], width=4, fill=dark, capstyle="round")

    # cart frame, drawn over the body: upright at the hips, rail along the back, chest strap
    if pet.cart:
        line([(ax + 6, ay - 4), (54, cby - 30), (102, cby - 28), (106, cby + 4)],
             width=5, fill=FRAME, capstyle="round", joinstyle="round")
        if in_cart:
            line([(104, by - 27), (104, by + 21)], width=5, fill=STRAP)

    # the paw she holds out to you (high five, and while the sign is up), in front of her chest
    if st in ("highfive", "pause"):
        line([(124, by + 12), (166, by - 2)], width=10, fill=dark, capstyle="round",
             tags=("paw",))
        oval(158, by - 11, 178, by + 7, fill=dark, outline="", tags=("paw",))
        oval(165, by - 6, 172, by + 1, fill=pink, outline="", tags=("paw",))   # toe bean

    # ears, head
    poly([(hx - 21, hy - 12), (hx - 25, hy - 36), (hx - 5, hy - 22)], fill=fur, outline="")
    poly([(hx + 13, hy - 20), (hx + 20, hy - 38), (hx + 26, hy - 15)], fill=fur, outline="")
    oval(hx - 24, hy - 22, hx + 24, hy + 22, fill=fur, outline="", tags=("head",))

    # eyes (shut when she naps, and when she grooms, like the real thing)
    ey = hy - 2
    if napping or st == "lick":
        for ex in (hx - 9, hx + 9):
            line([(ex - 6, ey), (ex, ey + 4), (ex + 6, ey)],
                 width=2, fill=EYE, smooth=True, capstyle="round", tags=("eyes_shut",))
    else:
        blink = frame % 90 < 4
        for ex in (hx - 9, hx + 9):
            if blink:
                line([(ex - 6, ey), (ex + 6, ey)], width=2, fill=EYE, capstyle="round")
            else:
                oval(ex - 5, ey - 7, ex + 5, ey + 7, fill=EYE, outline="", tags=("eyes_open",))
                oval(ex - 3, ey - 6, ex, ey - 3, fill="white", outline="")

    # nose, mouth, whiskers
    poly([(hx + 1, ey + 10), (hx + 11, ey + 10), (hx + 6, ey + 16)], fill=pink, outline="")
    if st in ("meow", "hairball"):
        oval(hx + 1, ey + 15, hx + 13, ey + 26, fill=MOUTH, outline="", tags=("mouth",))
        oval(hx + 4, ey + 21, hx + 11, ey + 26, fill=pink, outline="")
    elif st in ("lick", "milk", "grass"):
        oval(hx + 2, ey + 14, hx + 13, ey + 23, fill=pink, outline="", tags=("tongue",))
    for wy in (ey + 8, ey + 14):
        line([(hx + 13, wy), (hx + 32, wy - 3)], width=1, fill=dark)

    # the paw she's grooming, drawn last so it sits over her muzzle instead of behind it
    if st == "lick":
        line([(126, by + 14), (hx + 7, ey + 17)], width=10, fill=dark, capstyle="round")
        oval(hx - 1, ey + 9, hx + 17, ey + 25, fill=dark, outline="")
        oval(hx + 3, ey + 12, hx + 9, ey + 17, fill=pink, outline="")       # toe bean

    zoom_canvas(c, k)
    if napping:                                # drawn after the zoom, at final size
        for i in range(3):
            # drawn as lines, not text: antialiased text on the see-through colour key
            # leaves a pink fringe, plain lines don't
            size = (9 + i * 3) * k
            cx = fx(hx + 20 + i * 13) * k
            cy = (hy - 32 - i * 13 - (frame // 6) % 7) * k
            left, right, top, bottom = cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2
            c.create_line(left, top, right, top, left, bottom, right, bottom, fill="#7fb2e0",
                          width=max(2, round(2 * k)), capstyle="round", joinstyle="round",
                          tags=("zzz",))

    draw_bubble(c, pet, hy, k)


def zoom_canvas(c, k):
    """Blow the finished drawing up by k, line widths included, so nothing goes spindly."""
    if k == 1.0:
        return
    c.scale("all", 0, 0, k, k)
    for item in c.find_all():
        if c.type(item) in ("line", "oval", "polygon", "rectangle"):
            width = float(c.itemcget(item, "width"))
            if width:
                c.itemconfigure(item, width=width * k)


def draw_sign(c, cw, k, pet, now):
    """The sign she holds up during a break, drawn at final size after the zoom.
    k is her whole zoom (display scaling times the break zoom)."""
    end = pet.kind == "end"
    title, sub = STRINGS["sign_end" if end else "sign_break"]
    seconds_left = pet.pause_left(now)
    s = k / PAUSE_ZOOM                         # grows with her instead of popping in full size

    def font(px, *style):
        return (FONT, -max(8, round(px * s))) + style

    cx, top = cw / 2, 16 * s
    c.create_rectangle(cx - 140 * s, top, cx + 140 * s, top + 200 * s,
                       fill="white", outline=STRAP, width=6 * s, tags=("sign",))
    c.create_text(cx, top + 34 * s, text=title, fill=STRAP,
                  font=font(25 if end else 35, "bold"), tags=("sign",))
    c.create_text(cx, top + 68 * s, text=sub, fill=INK, font=font(19, "bold"), tags=("sign",))
    c.create_text(cx, top + 104 * s, text=STRINGS["sign_count"] % (seconds_left, pet.breath_word),
                  fill=MUTED, font=font(25, "bold"), tags=("sign",))
    c.create_line(cx - 108 * s, top + 130 * s, cx + 108 * s, top + 130 * s,
                  fill="#e4ded4", width=2 * s, tags=("sign",))
    c.create_text(cx, top + 164 * s, text=pet.coach_line(now), fill=INK, width=248 * s,
                  justify="center", font=font(16), tags=("sign",))


# --------------------------------------------------------------------------- the new look
# Pictures instead of shapes: SPRITES (bottom of the file) holds every pose as palette
# indices, drawn once as ginger with a lilac cart. Her coat and cart colour are a swap of
# palette entries, so four coats and three carts cost nothing extra. tools/sprites.py
# rebuilds the table from the sheets in art/.

SPRITE_SCALE = 2      # the pictures are stored at twice her size
CLEAR = 255           # palette index for "nothing here"
SIDE_RIGHT = 172      # where her nose ends when she faces right, same as the classic cat
# state: (picture in the cart, picture out of it)
CUTE = {"idle": ("c_idle", "n_idle"), "walk": ("c_idle", "n_idle"),
        "lick": ("c_lick", "n_lick"), "meow": ("c_meow", "n_meow"),
        "milk": ("c_milk", "n_milk"), "grass": ("c_milk", "n_milk"),
        "hairball": ("c_hairball", "n_hairball"), "highfive": ("c_paw", "n_paw"),
        "pause": ("c_paw", "n_paw"), "sleep": ("c_sleep", "n_sleep"),
        "away": ("c_sleep", "n_sleep"), "sit": ("n_sit", "n_sit"),
        "butt": ("c_back", "n_back"), "rest": ("n_sleep", "n_sleep")}
BOW, HAT, HAT_BAND, HEART = "#f27fa5", "#e8665a", "#fdf1e4", "#f2788f"
OUTLINE = "#3d2016"


def _hls(colour: str) -> tuple:
    return colorsys.rgb_to_hls(*(int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)))


def _hex(h: float, light: float, s: float) -> str:
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, light, s))


def sprite_palette(fur: str = DEFAULT_FUR, cart: str = DEFAULT_CART) -> tuple:
    """SPRITE_PALETTE in her coat and cart colour. She was drawn ginger with a lilac cart:
    every ginger tone moves to the chosen coat, keeping how much lighter or darker than
    her fur it was, and every lilac tone turns to the cart's hue. Outlines, eyes, cheeks,
    cream and metal stay as drawn."""
    if fur == DEFAULT_FUR and CART_COLOURS.get(cart) is None:
        return SPRITE_PALETTE
    gh, gl, gs = _hls(PALETTES[DEFAULT_FUR][0])
    th, tl, ts = _hls(PALETTES.get(fur, PALETTES[DEFAULT_FUR])[0])
    hue = CART_COLOURS.get(cart)
    out = []
    for colour in SPRITE_PALETTE:
        h, light, s = _hls(colour)
        if fur != DEFAULT_FUR and 0.03 <= h <= 0.13 and s > 0.4 and 0.3 < light < 0.86:
            colour = _hex(th, min(0.93, max(0.12, tl + light - gl)), min(1.0, ts * s / gs))
        elif hue is not None and 0.68 <= h <= 0.9 and s > 0.12 and light > 0.35:
            colour = _hex(hue, light, s)
        out.append(colour)
    return tuple(out)


_INDICES = {}


def sprite_indices(name: str) -> bytes:
    """One byte per pixel, row by row, CLEAR where she isn't."""
    if name not in _INDICES:
        _INDICES[name] = zlib.decompress(base64.b64decode(SPRITES[name][4]))
    return _INDICES[name]


def sprite_rgba(name: str, s: float, flip: bool = False, palette: tuple | None = None):
    """The picture at s times its stored size, as (width, height, PNG rows). Each pixel
    averages four samples, so lines stay smooth when she shrinks; it is either fully
    there or fully see-through, because the window's colour key can't do half."""
    w, h = SPRITES[name][:2]
    idx = sprite_indices(name)
    rgb = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in palette or SPRITE_PALETTE]
    ow, oh = max(1, round(w * s)), max(1, round(h * s))
    xs = [[min(w - 1, int((x + o) / s)) for o in (0.25, 0.75)] for x in range(ow)]
    if flip:
        xs.reverse()
    rows = bytearray()
    for oy in range(oh):
        rows.append(0)                          # PNG filter: none
        lines = [min(h - 1, int((oy + o) / s)) * w for o in (0.25, 0.75)]
        for pair in xs:
            r = g = b = n = 0
            for line in lines:
                for x in pair:
                    i = idx[line + x]
                    if i != CLEAR:
                        cr, cg, cb = rgb[i]
                        r, g, b, n = r + cr, g + cg, b + cb, n + 1
            rows += bytes((r // n, g // n, b // n, 255)) if n >= 2 else b"\0\0\0\0"
    return ow, oh, bytes(rows)


def png(w: int, h: int, rows: bytes) -> bytes:
    """A minimal RGBA PNG, which Tk reads natively."""
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


_IMAGES = {}


def sprite_image(c, name: str, k: float, flip: bool, palette: tuple):
    """A Tk image of one pose at zoom k, made once and kept."""
    k = max(0.25, round(k * 4) / 4)             # a handful of sizes, not one per frame
    key = (str(c.tk), name, k, flip, palette)
    if key not in _IMAGES:
        import tkinter as tk
        w, h, rows = sprite_rgba(name, k / SPRITE_SCALE, flip, palette)
        _IMAGES[key] = tk.PhotoImage(master=c, data=base64.b64encode(png(w, h, rows)))
    return _IMAGES[key]


def cute_sprite(pet, frame) -> str:
    """Which picture she is right now. She blinks now and then, like the classic cat."""
    name = CUTE.get(pet.state, CUTE["idle"])[0 if pet.cart and pet.state != "rest" else 1]
    if name.endswith("_idle") and frame % 90 < 4:
        name = name[:2] + "blink"
    return name


def draw_bow(c, x, y):
    for side in (-1, 1):
        c.create_polygon(x, y, x + side * 9, y - 6, x + side * 9, y + 6, fill=BOW,
                         outline=OUTLINE, width=1.5, tags=("bow",))
    c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=BOW, outline=OUTLINE, width=1.5,
                  tags=("bow",))


def draw_hat(c, x, y):
    c.create_arc(x - 15, y - 16, x + 15, y + 12, start=0, extent=180, fill=HAT,
                 outline=OUTLINE, width=1.5, style="chord", tags=("hat",))
    c.create_rectangle(x - 15, y - 3, x + 15, y + 2, fill=HAT_BAND, outline=OUTLINE,
                       width=1.5, tags=("hat",))
    c.create_oval(x - 4, y - 23, x + 4, y - 15, fill=HAT_BAND, outline=OUTLINE, width=1.5,
                  tags=("hat",))


def draw_heart(c, x, y):
    c.create_oval(x - 7, y - 5, x, y + 2, fill=HEART, outline="", tags=("heart",))
    c.create_oval(x, y - 5, x + 7, y + 2, fill=HEART, outline="", tags=("heart",))
    c.create_polygon(x - 7, y - 1, x + 7, y - 1, x, y + 8, fill=HEART, outline="",
                     tags=("heart",))


def draw_cute(c, pet, frame, k=1.0):
    """The new look: one picture per pose, the bowl, grass and hairball drawn around it."""
    c.delete("all")
    st = pet.state
    fur, dark, _ = pet.colours
    right = pet.dir >= 0 or st == "butt"       # her back looks the same either way
    fx = (lambda x: x) if right else (lambda x: W - x)
    palette = sprite_palette(pet.fur, pet.cart_colour)
    t = frame * 0.12
    name = cute_sprite(pet, frame)
    w, h, bx, by = (v / SPRITE_SCALE for v in SPRITES[name][:4])
    if st == "pause":
        bob = -pet.breath * 3                  # she breathes with you, 4-7-8
    elif st in ("sleep", "away", "rest", "butt"):
        bob = 0
    else:
        bob = round(math.sin(t * (2.2 if st == "walk" else 1.0)) * 1.2)
    top = GROUND - h + bob

    if st == "rest":                           # out of the cart, napping right beside it
        cw, ch = (v / SPRITE_SCALE for v in SPRITES["cart"][:2])
        c.create_image(8 if right else W - 8 - cw, GROUND - ch, anchor="nw",
                       tags=("sprite", "cart"),
                       image=sprite_image(c, "cart", k, not right, palette))
        left = 196 - w if right else W - 196
    elif st in ("butt", "pause"):              # facing you, or holding the sign up
        left = (W - w) / 2
    else:
        left = SIDE_RIGHT - w if right else W - SIDE_RIGHT
    c.create_image(left, top, anchor="nw", tags=("sprite", name),
                   image=sprite_image(c, name, k, not right, palette))

    def oval(x1, y1, x2, y2, **kw):
        a, b = fx(x1), fx(x2)
        c.create_oval(min(a, b), y1, max(a, b), y2, **kw)

    if st == "milk":
        x1, y1, x2, y2 = bowl_box(1)
        oval(x1, y1, x2, y2, fill=BOWL, outline=FRAME, width=2, tags=("bowl",))
        oval(x1 + 5, y1 + 2, x2 - 5, y2 - 6, fill=MILK, outline="", tags=("bowl",))
    elif st == "grass":
        for gx, gh, bend in ((140, 22, 6), (149, 30, -5), (158, 26, 8), (167, 18, -4)):
            c.create_line(fx(gx), GROUND - 2, fx(gx + bend), GROUND - gh, width=4, fill=GRASS,
                          capstyle="round", smooth=True, tags=("grass",))
    elif st == "hairball" and pet.progress > 0.6:
        oval(176, GROUND - 11, 196, GROUND - 1, fill=dark, outline="", tags=("hairball",))
        oval(180, GROUND - 12, 192, GROUND - 5, fill=fur, outline="", tags=("hairball",))

    ax = left + (bx if right else w - bx)      # between her ears, where things sit
    ay = top + by
    if "hat" in pet.wear:
        draw_hat(c, ax, ay + 3)
    if "bow" in pet.wear:
        draw_bow(c, ax + (10 if right else -10) if "hat" in pet.wear else ax, ay + 2)
    if pet.heart_until > pet.last_step:
        draw_heart(c, ax, top - 10)

    zoom_canvas(c, k)
    if st in ("sleep", "away", "rest"):        # drawn after the zoom, as lines (see draw())
        hx = left + w * 0.75 if right else left + w * 0.25
        for i in range(3):
            size = (9 + i * 3) * k
            cx = (hx + (i * 13 if right else -i * 13)) * k
            cy = (top - 6 - i * 13 - (frame // 6) % 7) * k
            x1, x2, y1, y2 = cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2
            c.create_line(x1, y1, x2, y1, x1, y2, x2, y2, fill="#7fb2e0",
                          width=max(2, round(2 * k)), capstyle="round", joinstyle="round",
                          tags=("zzz",))
    draw_bubble(c, pet, top + 14, k)      # draw_bubble sits it 42 above this


# --------------------------------------------------------------------------- her memory

def config_dir(platform: str = sys.platform, env=None, home: Path | None = None) -> Path:
    """Where she keeps her memory: the usual per-user config folder for each system."""
    env = os.environ if env is None else env
    home = Path.home() if home is None else Path(home)
    if platform.startswith("win"):
        base = env.get("APPDATA")
        return (Path(base) if base else home / "AppData" / "Roaming") / "kocicka"
    if platform == "darwin":
        return home / "Library" / "Application Support" / "kocicka"
    base = env.get("XDG_CONFIG_HOME")
    # the XDG spec says to ignore a relative path here
    return (Path(base) if base and base.startswith("/") else home / ".config") / "kocicka"


LEGACY_CONFIG = Path(__file__).with_name("kocka.json")   # where versions before 2026-10 kept it


def _read_json(path: Path) -> dict | None:
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None                            # missing or corrupt
    return cfg if isinstance(cfg, dict) else None


class Store:
    """Her memory on disk. Writes go to a temp file that then replaces the real one, so a
    crash mid-write never leaves half a file; the previous version stays as .bak."""

    def __init__(self, path: Path | None = None, legacy: Path | None = LEGACY_CONFIG):
        self.path = Path(path) if path else config_dir() / "kocka.json"
        self.backup = self.path.with_name(self.path.name + ".bak")
        self.legacy = legacy

    def load(self) -> dict:
        for candidate in (self.path, self.backup):
            cfg = _read_json(candidate)
            if cfg is not None:
                return cfg
        if self.legacy and self.legacy != self.path:
            cfg = _read_json(self.legacy)
            if cfg is not None:                # an older version kept it next to the script
                self.save(cfg)                 # copy it over; the old file is left alone
                return cfg
        return {}                              # nothing readable: she just asks again

    def save(self, cfg: dict) -> bool:
        """True if it reached the disk. A read-only folder is not an error: she runs on."""
        tmp = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # a temp name of its own every time, so two writers never trip over each other
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=self.path.name + ".",
                                       suffix=".tmp")
            with open(fd, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(cfg, ensure_ascii=False, indent=2))
                fh.flush()
                os.fsync(fh.fileno())
            if _read_json(self.path) is not None:   # never back up a broken file over a
                shutil.copy2(self.path, self.backup)  # good backup
            os.replace(tmp, self.path)
            return True
        except OSError:
            if tmp:
                with contextlib.suppress(OSError):
                    os.unlink(tmp)
            return False


# --------------------------------------------------------------------------- only one of her

def pid_alive(pid: int) -> bool:
    """True if a process with this id is still running."""
    if pid <= 0:
        return False
    if sys.platform.startswith("win"):
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
        k32.GetExitCodeProcess.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32))
        k32.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = k32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5        # access denied: it exists, not ours
        code = ctypes.c_uint32()
        try:
            return bool(k32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            k32.CloseHandle(handle)                    # 259 is STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True                                    # someone else's, but alive
    except OSError:
        return False
    return True


class FileLock:
    """A file holding the pid of the copy that is running. A lock left behind by a copy
    that crashed is noticed (that pid is gone) and taken over."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.held = False

    def acquire(self) -> bool:
        for _ in range(2):
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    pid = int(self.path.read_text(encoding="utf-8").strip())
                except (OSError, ValueError):
                    pid = 0
                if pid_alive(pid):
                    return False               # she is already on your screen
                with contextlib.suppress(OSError):
                    self.path.unlink()         # stale: the copy that wrote it is gone
                continue
            except OSError:
                return True                    # can't write a lock here: run anyway
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(str(os.getpid()))
            self.held = True
            return True
        return False

    def release(self) -> None:
        if self.held:
            self.held = False
            with contextlib.suppress(OSError):
                self.path.unlink()


class _Mutex:
    """Windows: a named mutex, which Windows drops by itself if she crashes."""

    def __init__(self, handle, k32):
        self.handle, self.k32 = handle, k32

    def release(self) -> None:
        if self.handle:
            self.k32.CloseHandle(self.handle)
            self.handle = None


def single_instance(lock_path: Path):
    """Something with a release() while this is the only copy running, None if another
    copy already is. A named mutex on Windows, a pid file everywhere else."""
    if not sys.platform.startswith("win"):
        lock = FileLock(lock_path)
        return lock if lock.acquire() else None
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateMutexW.restype = ctypes.c_void_p
    k32.CreateMutexW.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p)
    k32.CloseHandle.argtypes = (ctypes.c_void_p,)
    name = "Local\\kocicka-" +hashlib.sha1(str(Path(lock_path).resolve()).lower()
                                             .encode("utf-8")).hexdigest()[:16]
    handle = k32.CreateMutexW(None, False, name)
    if not handle:
        return _Mutex(None, k32)               # no mutex to be had: run anyway
    if ctypes.get_last_error() == 183:         # ERROR_ALREADY_EXISTS
        k32.CloseHandle(handle)
        return None
    return _Mutex(handle, k32)


def czech_count(n: int, key: str) -> str:
    """1, 2-4 or 5+ of something: Czech picks the word by the number."""
    one, few, many = STRINGS[key]
    return "%d %s" % (n, one if n == 1 else few if 1 < n < 5 else many)


def czech_days(n: int) -> str:
    return czech_count(n, "days")


def snooze_label() -> str:
    """The menu item, worded from SNOOZE so the two never disagree."""
    return STRINGS["menu_snooze"] % czech_count(max(1, round(SNOOZE / 60)), "minutes")


def greeting(cfg: dict, today: str) -> str:
    """Day one she introduces herself; after that she picks up where she left off."""
    name = cfg.get("name") or STRINGS["fallback_name"]
    hello = STRINGS["hello"] % name
    first, last = cfg.get("first_seen"), cfg.get("last_seen")
    if not first or first == today:
        return hello
    try:
        days = (date.fromisoformat(today) - date.fromisoformat(first)).days + 1
        gap = (date.fromisoformat(today) - date.fromisoformat(last)).days if last else 0
    except (TypeError, ValueError):
        return hello                           # dates she can't read: just say hello
    if gap >= 2:
        return STRINGS["missed_you"] % czech_days(gap)
    return STRINGS["day_n"] % days


def water_line(cfg: dict, today: str, hour: int) -> str | None:
    """Her afternoon nag about drinking, or nothing if it isn't warranted."""
    w = cfg.get("water")
    w = w if isinstance(w, dict) else {}
    drunk = w.get("count", 0) if w.get("date") == today else 0
    if not isinstance(drunk, int):
        drunk = 0
    if hour < 14 or drunk >= WATER_GOAL:
        return None
    if drunk == 0:
        return STRINGS["water_none"]
    return STRINGS["water_some"] % drunk


def _count(n) -> int:
    return n if isinstance(n, int) and not isinstance(n, bool) and n >= 0 else 0


def wellness(cfg: dict) -> dict:
    """Her wellness memory, tidied: points per day, the running total, what she has on.
    Anything odd on disk is dropped rather than trusted."""
    w = cfg.get("wellness")
    w = w if isinstance(w, dict) else {}
    days = w.get("days") if isinstance(w.get("days"), dict) else {}
    days = {d: _count(n) for d, n in days.items() if isinstance(d, str) and _count(n)}
    wear = w.get("wear") if isinstance(w.get("wear"), list) else []
    return {"days": days, "total": _count(w.get("total")) or sum(days.values()),
            "focus": w.get("focus"), "end": w.get("end"),
            "wear": [x for x in WEARABLES if x in wear],
            "cart": w.get("cart") if w.get("cart") in CART_COLOURS else DEFAULT_CART}


def unlocked(total: int, item: str) -> bool:
    need = dict(REWARDS).get(item, 0)
    return total >= need


def streak(days: dict, today: str) -> int:
    """Days in a row with at least one point. A weekend without any doesn't break it,
    and neither does today before you've had the chance."""
    try:
        d = date.fromisoformat(today)
    except (TypeError, ValueError):
        return 0
    if not days.get(today):
        d -= timedelta(days=1)
    n = 0
    while True:
        if days.get(d.isoformat()):
            n += 1
        elif d.weekday() < 5:
            return n
        d -= timedelta(days=1)


def week(days: dict, today: str) -> str:
    """The last seven days, oldest first, each as its weekday and its points."""
    try:
        d = date.fromisoformat(today)
    except (TypeError, ValueError):
        return ""
    names = STRINGS["weekdays"]
    return STRINGS["week_join"].join("%s %d" % (names[x.weekday()], days.get(x.isoformat(), 0))
                      for x in (d - timedelta(days=i) for i in range(6, -1, -1)))


# --------------------------------------------------------------------------- the app, minus Tk

_BUSY = ("walk", "pause", "hairball")   # states that move enough to need every frame


class Companion:
    """Everything the window decides, without the window: the day, her memory, clicks,
    the menu, when to hide, when to redraw, where to stand. run() is only Tk glue around
    this, so all of it can be tested without a display."""

    def __init__(self, cfg: dict, store: Store, pet: Pet, today: str,
                 now: float, scale: float = 1.0, area: tuple | None = None):
        self.cfg, self.store, self.pet = cfg, store, pet
        self.today = today
        self.scale = scale
        self.t0 = now            # animation clock, so frames advance with time, not ticks
        self.away = False
        self.hidden = False
        self.asking = False      # the "one thing" question is on screen
        self.day_start = pet.total
        self.end_not_before = 0.0
        self.last_slow = -1e18
        self.last_key = None
        self.warned = False
        self.drag_from, self.dragged = None, 0.0
        self.area = area or (0, 0, int(pet.screen_w * scale), H)
        self.saved_work = now
        self.end_at = 0.0        # when today's end-of-day sign went up, 0 = not yet
        self.restore_work(now)
        pet.look = cfg.get("look") if cfg.get("look") in LOOKS else "new"
        self.dress()

    # memory
    def save(self, now: float) -> bool:
        ok = self.store.save(self.cfg)
        if not ok and not self.warned:         # tell you once, then stop going on about it
            self.warned = True
            self.pet.speak(STRINGS["cant_save"], now, 9)
        return ok

    # work time, kept across a restart the same day
    def remember_work(self, now: float) -> bool:
        self.saved_work = now
        self.cfg["work"] = {"date": self.today, "at": now, "worked": round(self.pet.worked, 1),
                            "today": round(self.worked_today(), 1)}
        return self.save(now)

    def restore_work(self, now: float) -> None:
        """Pick up today's count where the last run left it. Yesterday's starts fresh, and
        a gap longer than AWAY_AFTER between runs was a break."""
        w = self.cfg.get("work")
        if not isinstance(w, dict) or w.get("date") != self.today:
            return
        nums = [w.get(k) for k in ("at", "worked", "today")]
        if not all(isinstance(n, (int, float)) and not isinstance(n, bool) and n >= 0
                   for n in nums):
            return
        at, worked, today = nums
        self.pet.total += today
        if 0 <= now - at <= AWAY_AFTER:
            self.pet.worked = min(float(worked), float(PAUSE_EVERY))

    # wellness points: one for each real thing she already keeps an eye on
    def dress(self) -> None:
        """Put on her what you've picked and unlocked."""
        w = wellness(self.cfg)
        self.pet.wear = tuple(x for x in w["wear"] if unlocked(w["total"], x))
        self.pet.cart_colour = w["cart"] if unlocked(w["total"], w["cart"]) else DEFAULT_CART

    def award(self, now: float, mark: str = "") -> bool:
        """One point, for good. mark ("focus", "end") makes it a once-a-day point. Only
        remembered here; the caller saves, so one action is one write."""
        w = wellness(self.cfg)
        if mark and w.get(mark) == self.today:
            return False
        if mark:
            w[mark] = self.today
        before = w["total"]
        w["total"] = before + 1
        w["days"][self.today] = w["days"].get(self.today, 0) + 1
        for old in sorted(w["days"])[:-62]:      # two months is plenty for a week view
            del w["days"][old]
        self.cfg["wellness"] = w
        self.pet.heart_until = now + 2.5
        for item, need in REWARDS:
            if before < need <= w["total"]:
                self.pet.speak(STRINGS["unlocked"] % STRINGS["reward_won"][item], now, 6)
        return True

    def set_look(self, look: str, now: float) -> None:
        if look in LOOKS:
            self.pet.look = self.cfg["look"] = look
            self.save(now)

    def toggle_wear(self, item: str, now: float) -> bool:
        w = wellness(self.cfg)
        if item not in WEARABLES or not unlocked(w["total"], item):
            return False
        w["wear"] = [x for x in WEARABLES if (x in w["wear"]) != (x == item)]
        self.cfg["wellness"] = w
        self.dress()
        self.save(now)
        return True

    def set_cart_colour(self, name: str, now: float) -> bool:
        w = wellness(self.cfg)
        if name not in CART_COLOURS or not unlocked(w["total"], name):
            return False
        w["cart"] = name
        self.cfg["wellness"] = w
        self.dress()
        self.save(now)
        return True

    def points_menu(self) -> list:
        """What the points submenu shows, as (kind, label, key, enabled, on) rows; run()
        only turns them into menu entries. kind: info, sep, wear, cart."""
        w = wellness(self.cfg)
        total = w["total"]
        rows = [("info", STRINGS["points_total"] % (czech_count(total, "points"),
                                                    czech_days(streak(w["days"], self.today))),
                 "", False, False),
                ("info", week(w["days"], self.today), "", False, False),
                ("info", STRINGS["points_how"], "", False, False),
                ("sep", "", "", False, False)]
        labels, need = STRINGS["reward_labels"], dict(REWARDS)
        for kind, keys, on in (("wear", WEARABLES, lambda x: x in w["wear"]),
                               ("cart", tuple(CART_COLOURS), lambda x: x == w["cart"])):
            for x in keys:
                ok = unlocked(total, x)
                label = labels[x] if ok else STRINGS["locked"] % (labels[x], need[x])
                rows.append((kind, label, x, ok, on(x)))
        if self.pet.look != "new":
            rows.append(("info", STRINGS["new_look_only"], "", False, False))
        return rows

    # the day
    def worked_today(self) -> float:
        return self.pet.total - self.day_start

    def new_day(self, today: str, now: float) -> None:
        """Past midnight: yesterday's one thing is yesterday's, and she'll ask again."""
        self.today = today
        self.day_start = self.pet.total
        self.end_not_before = 0.0
        self.end_at = 0.0
        self.cfg["last_seen"] = today
        self.save(now)

    def focus(self) -> dict:
        """Today's one thing, or {} if she hasn't asked yet today."""
        f = self.cfg.get("focus")
        return f if isinstance(f, dict) and f.get("date") == self.today else {}

    def focus_label(self) -> str:
        f = self.focus()
        if not f.get("text"):
            return STRINGS["focus_none"]
        return (STRINGS["focus_done"] if f.get("done") else STRINGS["focus_today"]) + f["text"]

    def wants_focus(self, hour: int) -> bool:
        return (not self.focus() and not self.asking and 6 <= hour < WORK_END
                and not self.pet.asleep(hour) and not self.away and not self.hidden
                and self.pet.state != "pause")

    def set_focus(self, text: str | None, now: float) -> None:
        """An empty or cancelled answer is a fine answer; she won't ask again today."""
        self.asking = False
        self.cfg["focus"] = {"date": self.today, "text": (text or "").strip()[:60],
                             "done": False}
        self.save(now)

    def toggle_focus(self, now: float) -> bool:
        f = self.focus()
        if not f.get("text"):
            return False
        f["done"] = not f.get("done")
        self.cfg["focus"] = f
        self.pet.speak(STRINGS["focus_proud" if f["done"] else "focus_undo"], now, 5)
        if f["done"]:
            self.award(now, "focus")           # once a day, and unticking takes nothing back
        self.save(now)
        return True

    def drank(self, now: float) -> None:
        w = self.cfg.get("water")
        if not isinstance(w, dict) or w.get("date") != self.today:
            w = {"date": self.today, "count": 0}
        w["count"] = (w.get("count") if isinstance(w.get("count"), int) else 0) + 1
        self.cfg["water"] = w
        left = WATER_GOAL - w["count"]
        self.pet.speak(STRINGS["water_count"] % (w["count"], left) if left > 0
                       else STRINGS["water_done"] % w["count"], now, 5)
        if w["count"] <= WATER_GOAL:
            self.award(now)                    # up to the day's goal; more is fine, just free
        self.save(now)

    def set_cart(self, on: bool, now: float) -> None:
        self.pet.cart = on
        if on and self.pet.state == "sit":
            self.pet.do("idle", now, 2)
        self.cfg["cart"] = on
        self.save(now)

    def rename(self, chosen: dict | None, now: float) -> bool:
        if not chosen:                         # closed with X: nothing changes
            return False
        self.cfg.update(chosen)
        self.pet.fur = self.cfg.get("fur", DEFAULT_FUR)
        self.save(now)
        self.pet.speak(STRINGS["renamed"] % self.cfg["name"], now, 5)
        return True

    # breaks
    def end_due(self, now: float, hour: int) -> bool:
        """The end-of-day sign, once, after real work today, never into an empty room."""
        return (self.cfg.get("ended") != self.today and hour >= WORK_END
                and not self.pet.asleep(hour) and not self.away and not self.hidden
                and self.pet.state != "pause" and now >= self.end_not_before
                and self.worked_today() >= END_AFTER_WORK)

    def skip(self, now: float) -> None:
        """Skip this break: put the sign down now, or skip the one that is coming."""
        p = self.pet
        if p.state == "pause":
            p.finish_pause(now)
        p.worked, p.due_at = 0.0, 0.0
        p.speak(STRINGS["skipped"], now, 4)

    def snooze(self, now: float) -> None:
        """SNOOZE more seconds on the clock, then the sign comes back. Never sooner than
        the hour of work would have brought it."""
        p = self.pet
        if p.state == "pause" and p.kind == "end":
            p.finish_pause(now, lie_down=False)
            self.cfg.pop("ended", None)
            self.end_not_before = now + SNOOZE
            self.save(now)
        elif p.state == "pause":
            p.finish_pause(now)
            p.due_at = now + SNOOZE
        elif p.due_at or PAUSE_EVERY - p.worked <= SNOOZE:
            p.due_at = now + SNOOZE
        minutes = czech_count(max(1, round(SNOOZE / 60)), "minutes")
        p.speak(STRINGS["snoozed"] % minutes, now, 4)

    # the mouse
    def press(self, x_root: float) -> None:
        self.drag_from, self.dragged = x_root, 0.0

    def drag(self, x_root: float) -> None:
        if self.drag_from is None:
            return
        d = x_root - self.drag_from
        self.dragged += abs(d)
        self.pet.x = min(self.pet.max_x, max(0, self.pet.x + d / self.scale))
        self.drag_from = x_root

    def release(self, x: float, y: float, now: float) -> str:
        """A click (not a drag) at canvas pixel x, y. Returns what it did."""
        dragged, self.drag_from = self.dragged, None
        if dragged >= 5:
            return "drag"
        p = self.pet
        if p.state == "pause":
            if p.kind == "end":                # the end-of-day sign goes when you say so
                p.finish_pause(now)
                return "dismissed"
            return "held"                      # the hourly one runs out (or use the menu)
        ux, uy = x / self.scale, y / self.scale
        x1, y1, x2, y2 = bowl_box(p.dir)
        if p.state == "milk" and x1 - 4 <= ux <= x2 + 4 and y1 - 4 <= uy <= y2 + 4:
            self.drank(now)                    # you clinked her bowl, so you drank too
            return "drank"
        p.do("highfive", now, 3)
        p.chatter(now)
        return "highfive"

    # time
    def needs_slow(self, now: float) -> bool:
        return now - self.last_slow >= SLOW_EVERY

    def slow(self, now: float, hour: int, today: str, idle: float, fullscreen: bool,
             area: tuple | None = None) -> bool:
        """The once-a-second checks. Returns True when she should show or hide."""
        self.last_slow = now
        self.away = idle > AWAY_AFTER
        if today != self.today:                # she ran past midnight
            self.new_day(today, now)
        if area:
            self.area = area
            self.pet.screen_w = (area[2] - area[0]) / self.scale
            self.pet.x = min(self.pet.x, self.pet.max_x)
        self.pet.extra = [w for w in (water_line(self.cfg, today, hour),) if w]
        changed = fullscreen != self.hidden
        self.hidden = fullscreen
        if self.end_due(now, hour):
            self.cfg["ended"] = self.today
            self.save(now)
            self.pet.start_pause(now, "end")
            self.end_at = now
        if self.away and self.end_at and now - self.end_at <= END_GRACE + AWAY_AFTER:
            if self.award(now, "end"):         # she said stop, and you did
                self.save(now)
            self.end_at = 0.0
        if now - self.saved_work >= SAVE_WORK_EVERY:
            self.remember_work(now)
        return changed

    def frame(self, now: float) -> int:
        """Animation frame. Counted from time, so a slower tick doesn't slow her down;
        coarser while she naps, since nothing on her moves fast then."""
        n = int((now - self.t0) * 1000 // TICK)
        if self.pet.state in ("sleep", "away"):
            return n - n % 6
        return n if self.pet.state in _BUSY or self.drag_from is not None else n - n % 2

    def tick_ms(self) -> int:
        if self.hidden:
            return TICK_HIDDEN
        if self.drag_from is not None or self.pet.state in _BUSY:
            return TICK
        return TICK_SLEEP if self.pet.state in ("sleep", "away") else TICK * 2

    def advance(self, now: float, hour: int) -> bool:
        """Step her on. True when what you'd see changed, so it's worth a redraw."""
        p = self.pet
        p.step(now, hour, self.away, self.hidden)
        if p.completed:
            if p.completed == "break" and self.award(now):   # all thirty seconds of it
                self.save(now)
            p.completed = ""
        if self.hidden:
            return False
        key = (self.frame(now), p.state, p.dir, p.cart, p.fur, round(p.x, 1), round(p.roll, 1),
               p.look, p.wear, p.cart_colour, p.heart_until > now,
               p.say, round(p.zoom(now), 3), p.pause_left(now) if p.state == "pause" else 0,
               p.breath_word, round(p.breath, 2), p.coach_line(now), round(p.progress, 1),
               self.area, self.scale)
        if key == self.last_key:
            return False
        self.last_key = key
        return True

    def layout(self, now: float) -> tuple:
        """(k, extra, width, height, x, y): her zoom, sign headroom and window geometry,
        standing on the bottom of the work area and growing around her, not off to a side."""
        k = self.pet.zoom(now) * self.scale
        extra = PAUSE_EXTRA if self.pet.state == "pause" else 0
        cw, ch = int(W * k), int((H + extra) * k)
        left, _, right, bottom = self.area
        x = left + int(self.pet.x * self.scale - (cw - W * self.scale) / 2)
        x = min(max(left, x), max(left, right - cw))
        return k, extra, cw, ch, x, bottom - ch


# --------------------------------------------------------------------------- windows

def welcome(root, cfg=None, scale=1.0):
    """Pick a colour and a name, with her rolling along live underneath. Returns the
    choice, or None if the window was closed with X (nothing changes then)."""
    import tkinter as tk

    cfg = dict(cfg or {})
    chosen = {"name": cfg.get("name", ""), "fur": cfg.get("fur", DEFAULT_FUR),
              "cart": cfg.get("cart", True)}
    result = {}
    win = tk.Toplevel(root)
    win.title(STRINGS["welcome_title"])
    win.resizable(False, False)
    win.configure(bg=PAPER)

    tk.Label(win, text=STRINGS["welcome_head"], bg=PAPER, fg=INK,
             font=(FONT, 15, "bold")).pack(pady=(18, 0))
    tk.Label(win, text=STRINGS["welcome_sub"], bg=PAPER, fg=MUTED,
             font=(FONT, 10)).pack(pady=(2, 4))

    preview = tk.Canvas(win, width=int(W * scale), height=int(H * scale), bg=PAPER,
                        highlightthickness=0)
    preview.pack()
    demo = Pet(1000)                           # her own little stand-in: the real cat
    demo.state, demo.cart = "walk", chosen["cart"]   # doesn't change until you say so
    demo.look = cfg.get("look") if cfg.get("look") in LOOKS else "new"
    fur_var = tk.StringVar(value=chosen["fur"])
    anim = {"frame": 0}

    def spin():
        if not win.winfo_exists():
            return
        demo.roll += SPEED
        demo.fur = fur_var.get()
        anim["frame"] += 1
        draw(preview, demo, anim["frame"], scale)
        win.after(TICK, spin)

    row = tk.Frame(win, bg=PAPER)
    row.pack(pady=(0, 10))
    for key, label in STRINGS["fur_labels"]:
        tk.Radiobutton(row, text=label, value=key, variable=fur_var, bg=PAPER, fg=INK,
                       activebackground=PAPER, selectcolor="white",
                       font=(FONT, 10)).pack(side="left", padx=4)

    tk.Label(win, text=STRINGS["welcome_name"], bg=PAPER, fg=INK, font=(FONT, 10)).pack()
    entry = tk.Entry(win, font=(FONT, 12), justify="center", width=18)
    entry.insert(0, chosen["name"])
    entry.pack(pady=(4, 12))
    entry.focus_set()

    def done(*_):
        chosen["name"] = entry.get().strip()[:14] or STRINGS["fallback_name"]
        chosen["fur"] = fur_var.get()
        result.update(chosen)
        win.destroy()

    tk.Button(win, text=STRINGS["welcome_go"], font=(FONT, 11, "bold"), bg="#e8a75c",
              activebackground="#d99546", relief="flat", padx=18, pady=6,
              command=done).pack(pady=(0, 18))
    win.bind("<Return>", done)
    win.protocol("WM_DELETE_WINDOW", win.destroy)   # X means cancel

    spin()
    win.update_idletasks()
    win.geometry("+%d+%d" % ((win.winfo_screenwidth() - win.winfo_width()) // 2,
                             (win.winfo_screenheight() - win.winfo_height()) // 3))
    win.grab_set()
    root.wait_window(win)
    return result or None


def ask_focus(root, answer):
    """Once a day she asks for the one thing that matters. Empty answer is a fine answer.
    Returns at once, so she keeps ticking while you think; answer(text) gets what you
    typed, or None if you closed the window."""
    import tkinter as tk

    win = tk.Toplevel(root)
    win.title(STRINGS["focus_title"])
    win.resizable(False, False)
    win.configure(bg=PAPER)
    win.attributes("-topmost", True)
    tk.Label(win, text=STRINGS["focus_ask"], bg=PAPER, fg=INK, wraplength=320,
             font=(FONT, 11)).pack(padx=18, pady=(16, 8))
    entry = tk.Entry(win, font=(FONT, 12), justify="center", width=28)
    entry.pack(padx=18)
    entry.focus_set()

    def close(text):
        if win.winfo_exists():
            win.destroy()
            answer(text)

    tk.Button(win, text=STRINGS["focus_ok"], font=(FONT, 10, "bold"), bg="#e8a75c",
              activebackground="#d99546", relief="flat", padx=14, pady=4,
              command=lambda: close(entry.get())).pack(pady=(10, 16))
    win.bind("<Return>", lambda _e: close(entry.get()))
    win.bind("<Escape>", lambda _e: close(None))
    win.protocol("WM_DELETE_WINDOW", lambda: close(None))
    win.update_idletasks()
    win.geometry("+%d+%d" % ((win.winfo_screenwidth() - win.winfo_width()) // 2,
                             (win.winfo_screenheight() - win.winfo_height()) // 3))
    return win


def run(argv=()):
    import tkinter as tk

    set_dpi_awareness()                        # before the first window, or it's too late
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    try:
        root.attributes("-transparentcolor", KEY)
        backdrop = KEY
    except tk.TclError:
        backdrop = PAPER                       # no colour keying here: a soft card, not hot pink
    root.configure(bg=backdrop)
    scale = min(4.0, max(1.0, root.winfo_fpixels("1i") / 96.0))

    root.withdraw()                            # ask before she shows up, not over her
    store = Store()
    lock = single_instance(store.path.with_name("kocka.lock"))
    if lock is None:                           # she is already on your screen
        root.destroy()
        return
    cfg = store.load()
    if not cfg.get("name"):                    # asked on the very first run, until answered
        cfg.update(welcome(root, cfg, scale) or {})

    now, today = time.time(), date.today().isoformat()
    hello = greeting(cfg, today)
    cfg.setdefault("first_seen", today)
    cfg["last_seen"] = today
    area = work_area(root.winfo_screenwidth(), root.winfo_screenheight())
    pet = Pet((area[2] - area[0]) / scale)
    pet.cart, pet.fur = cfg.get("cart", True), cfg.get("fur", DEFAULT_FUR)
    pet.speak(hello, now, 6)
    app = Companion(cfg, store, pet, today, now, scale, area)   # picks up today's work
    app.save(now)
    root.deiconify()

    if "--demo" in argv:                       # so you don't have to wait an hour to see it
        pet.next_line, pet.worked = time.time() + 3, PAUSE_EVERY - 12
    c = tk.Canvas(root, width=W, height=H, bg=backdrop, highlightthickness=0)
    c.pack()
    shown = {"geometry": "", "extra": 0}       # what is on screen; extra = how far the sign
                                               # pushed her down, so clicks still line up

    menu = tk.Menu(root, tearoff=0)
    cart_var = tk.BooleanVar(value=pet.cart)

    def refresh_menu():
        menu.entryconfigure(0, label=cfg.get("name") or STRINGS["fallback_name"])
        menu.entryconfigure(1, label=app.focus_label())

    def rename():
        if app.rename(welcome(root, cfg, scale), time.time()):
            refresh_menu()

    def act(fn):
        return lambda: fn(time.time())

    menu.add_command(state="disabled")                                      # 0: her name
    menu.add_command(command=lambda: app.toggle_focus(time.time()) and refresh_menu())  # 1
    menu.add_separator()
    menu.add_command(label=STRINGS["menu_come"], command=lambda: pet.do("walk", time.time(), 4))
    menu.add_command(label=STRINGS["menu_paw"],
                     command=lambda: pet.do("highfive", time.time(), 4))
    menu.add_command(label=STRINGS["menu_milk"], command=lambda: pet.do("milk", time.time()))
    menu.add_command(label=STRINGS["menu_drank"], command=act(app.drank))
    menu.add_command(label=STRINGS["menu_say"], command=act(pet.chatter))
    menu.add_separator()
    menu.add_command(label=STRINGS["menu_break"], command=act(pet.start_pause))
    menu.add_command(label=STRINGS["menu_skip"], command=act(app.skip))
    menu.add_command(label=snooze_label(), command=act(app.snooze))
    menu.add_separator()
    menu.add_checkbutton(label=STRINGS["menu_cart"], variable=cart_var,
                         command=lambda: app.set_cart(cart_var.get(), time.time()))
    look_var = tk.StringVar(value=pet.look)
    looks = tk.Menu(menu, tearoff=0)
    for value in LOOKS:
        looks.add_radiobutton(label=STRINGS["look_" + value], value=value, variable=look_var,
                              command=lambda: app.set_look(look_var.get(), time.time()))
    menu.add_cascade(label=STRINGS["menu_look"], menu=looks)
    points = tk.Menu(menu, tearoff=0)
    picked = {}                                # the menu's own variables, kept alive

    def fill_points():
        points.delete(0, "end")
        picked.clear()
        for kind, label, key, ok, on in app.points_menu():
            state = "normal" if ok else "disabled"
            if kind == "info":
                points.add_command(label=label, state="disabled")
            elif kind == "sep":
                points.add_separator()
            elif kind == "wear":
                picked[key] = tk.BooleanVar(value=on)
                points.add_checkbutton(label=label, variable=picked[key], state=state,
                                       command=lambda x=key: app.toggle_wear(x, time.time()))
            else:
                picked.setdefault("cart", tk.StringVar(value=""))
                if on:
                    picked["cart"].set(key)
                points.add_radiobutton(label=label, value=key, variable=picked["cart"],
                                       state=state,
                                       command=lambda x=key: app.set_cart_colour(x, time.time()))

    points.configure(postcommand=fill_points)
    menu.add_cascade(label=STRINGS["menu_points"], menu=points)
    menu.add_command(label=STRINGS["menu_rename"], command=rename)
    menu.add_command(label=STRINGS["menu_close"], command=root.destroy)   # saved below
    refresh_menu()

    def open_menu(e):
        refresh_menu()                         # the date may have changed under it
        menu.tk_popup(e.x_root, e.y_root)

    c.bind("<ButtonPress-1>", lambda e: app.press(e.x_root))
    c.bind("<B1-Motion>", lambda e: app.drag(e.x_root))
    c.bind("<ButtonRelease-1>", lambda e: app.release(e.x, e.y - shown["extra"], time.time()))
    c.bind("<Button-3>", open_menu)
    if root.tk.call("tk", "windowingsystem") == "aqua":
        c.bind("<Button-2>", open_menu)        # macOS Tk reports the right button as 2

    def render(now):
        k, extra, cw, ch, x, y = app.layout(now)
        c.config(width=cw, height=ch)
        draw(c, pet, app.frame(now), k)
        shown["extra"] = int(extra * k)
        if extra:
            c.move("all", 0, extra * k)           # push her down, sign goes in above her
            draw_sign(c, cw, k, pet, now)
        geometry = "%dx%d+%d+%d" % (cw, ch, x, y)
        if geometry != shown["geometry"]:
            root.geometry(geometry)
            shown["geometry"] = geometry

    def tick():
        now, hour = time.time(), datetime.now().hour
        if app.needs_slow(now):
            area = work_area(root.winfo_screenwidth(), root.winfo_screenheight())
            if app.slow(now, hour, date.today().isoformat(), idle_seconds(),
                        fullscreen_in_front(), area):
                (root.withdraw if app.hidden else root.deiconify)()
            if app.wants_focus(hour):          # a new day, or the morning finally came
                app.asking = True              # she keeps ticking while you answer
                ask_focus(root, lambda text: (app.set_focus(text, time.time()),
                                              refresh_menu()))
        if app.advance(now, hour):
            render(now)
        root.after(app.tick_ms(), tick)

    tick()
    try:
        root.mainloop()
    finally:
        app.remember_work(time.time())         # so a restart today picks up the count
        lock.release()


# --------------------------------------------------------------------------- self-check

def smoke() -> None:
    """A quick check that needs nothing but this file, for people who only have KOCICKA.md."""
    random.seed(1)
    p, now = Pet(1920, x=0), 1_000_000.0
    p.last_step = now
    for i in range(1, 3001):
        p.step(now + i * 0.5, 12)
        if not 0 <= p.x <= p.max_x:
            raise AssertionError("she rolled off the screen: %r" % p.x)
    if abs(p.worked - 1500.0) > 1e-6:
        raise AssertionError("work time was not counted: %r" % p.worked)
    with tempfile.TemporaryDirectory() as folder:
        store = Store(Path(folder) / "kocka.json", legacy=None)
        if not store.save({"name": "Micka"}) or store.load() != {"name": "Micka"}:
            raise AssertionError("she could not remember her name")


def selftest() -> int:
    """smoke(), then the full tests/ suite when it sits next to this file."""
    smoke()
    tests = Path(__file__).resolve().with_name("tests")
    if tests.is_dir():
        import unittest
        suite = unittest.defaultTestLoader.discover(str(tests))
        if not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful():
            return 1
    print("ok")
    return 0


# --- sprites: generated by tools/sprites.py, do not edit by hand ---
SPRITE_PALETTE = (
    "#fdb058", "#fee6c5", "#441903", "#d5722c", "#d4d4d5", "#d1a5cd", "#c06228", "#d596a1",
    "#78726e", "#9c7d85", "#f7c68e", "#e5e0e7", "#612b1a", "#fdab80", "#733f26", "#f39c4f",
    "#8e5836", "#fed9aa", "#bd72a8", "#92491b", "#665040", "#af551c", "#e08e48", "#492c12",
    "#cbc1c4", "#2d0b01", "#aa6136", "#b28a90", "#edf2f5", "#d78d7f", "#ca8cbf", "#000000",
)
SPRITES = {   # name: (width, height, bow x, bow y, zlib'd palette indices)
    "c_idle": (199, 230, 138, 9,
        "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"
        "nN+04siXJv4ME+N3DUk5in5/f/8PqekxHg=="),
    "c_blink": (199, 230, 139, 10,
        "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"
        "WFrw/X/XEK2RYOzb/Q9rBPST"),
    "c_meow": (199, 229, 139, 10,
        "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"
        "jiPpm5gwXqklOcT/Pr/5Cw=="),
    "c_lick": (199, 230, 139, 10,
        "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"),
    "c_milk": (232, 166, 146, 16,
        "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"
        "4+cenGtyLn8Xv53yf8GXRFQ="),
    "c_hairball": (224, 184, 187, 7,
        "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"),
    "c_paw": (216, 218, 138, 7,
        "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"
        "3790jynXsVLeKhHU/xsvj5U="),
    "c_sleep": (221, 161, 181, 13,
        "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"
        "/YSXZ7wFWlEfetUbUgG4d3mrvCH/ANCHmFI="),
    "n_idle": (229, 208, 142, 18,
        "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"),
    "n_blink": (226, 207, 143, 18,
        "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"),
    "n_sit": (192, 210, 106, 19,
        "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"),
    "n_lick": (197, 207, 116, 18,
        "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"),
    "n_meow": (226, 208, 138, 18,
        "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"
        "1w=="),
    "n_milk": (258, 162, 50, 55,
        "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"),
    "n_hairball": (259, 171, 169, 10,
        "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"
        "v/2eb5xd0id+S5Fb0jrL/c1fnV/P3cB/j6UQxw=="),
    "n_paw": (212, 210, 99, 22,
        "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"),
    "n_sleep": (262, 163, 166, 21,
        "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"),
    "c_back": (156, 230, 59, 18,
        "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"
        "KlA="),
    "cart": (180, 97, 125, 1,
        "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"),
    "n_back": (138, 208, 53, 16,
        "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"
        "eiAomf6kbqS7lTypyTJ+/HfjuD+R18/xF/1O2WU="),
}
# --- end of sprites ---


if __name__ == "__main__":
    sys.exit(selftest()) if "--selftest" in sys.argv else run(sys.argv[1:])

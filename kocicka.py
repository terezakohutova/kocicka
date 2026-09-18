#!/usr/bin/env python3
"""Kocicka - a desktop cat in a wheelchair who keeps you company and looks after you.

stdlib only (tkinter + ctypes), no assets, no install, nothing leaves your machine.
On the first run she asks for a name and a colour; after that she remembers both in
kocka.json and comes back the same cat. She notices when you step away, shuts up when
you share your screen, stops you for a stretch once an hour of actual work, and calls
it a day when the day is done.
  run:        python kocicka.py
  demo:       python kocicka.py --demo        (speeds the timers up so you see it now)
  self-check: python kocicka.py --selftest
"""
import ctypes
import json
import math
import random
import sys
import time
from datetime import date, datetime
from pathlib import Path

W, H = 200, 230      # window size: cat in the bottom, speech bubble on top
GROUND = 210         # floor line inside the window
TASKBAR = 60         # ponytail: fixed taskbar margin, bump it if she overlaps your taskbar
SPEED = 1.6          # px per frame while rolling
TICK = 40            # ms per frame
SLOW = 25            # how many frames between the expensive Windows checks
LINE_EVERY = (180, 420)   # seconds between her little pep talks
PAUSE_EVERY = 3600        # seconds of ACTUAL work between the big stop-everything breaks
PAUSE_SECS = 30           # how long a break lasts
END_SECS = 45             # how long the end-of-day wind-down lasts
PAUSE_ZOOM = 2.0          # how much bigger she gets while holding the sign
PAUSE_EXTRA = 60          # headroom the window grows so the sign clears her ears
COACH_EVERY = 6           # seconds each stretch prompt stays up during the countdown
AWAY_AFTER = 300          # no keyboard or mouse for this long and she assumes you left
WORK_END = 16             # hour she calls it a day and tells you to close the laptop
WATER_GOAL = 6            # glasses before she stops nagging
NIGHT = (22, 7)           # sleeps from 22:00 to 07:00

PALETTES = {         # fur, shading/legs, nose
    "zrzava": ("#e8a75c", "#b9702e", "#f2a0a8"),
    "seda": ("#a8b2c1", "#6f7d91", "#e0a3ad"),
    "smetanova": ("#f0dfc2", "#c9ab82", "#f2a0a8"),
    "cerna": ("#55555f", "#33333a", "#e6909c"),
}
PALETTE_LABELS = (("zrzava", "zrzavá"), ("seda", "šedá"),
                  ("smetanova", "smetanová"), ("cerna", "černá"))
FUR, DARK, PINK = PALETTES["zrzava"]
EYE, MOUTH = "#3b2b20", "#8a3a45"
KEY = "#ff00ff"      # transparent colour key (Windows only)

WHEEL_R = 20         # rear-wheel cart for a cat whose back legs don't carry her
FRAME, TIRE, RIM, STRAP = "#9aa0a8", "#3f3f46", "#c9ccd1", "#d2533f"
BOWL, MILK, GRASS, STAR = "#cfd6de", "#fdfdfb", "#7ba05b", "#d97757"

CONFIG = Path(__file__).with_name("kocka.json")   # her name and colour, kept between runs
FALLBACK_NAME = "Kočička"
PAPER, INK, MUTED = "#faf7f2", "#2b2b2b", "#6b6b6b"

# everything she says: encouraging, funny, and always from a cat's point of view
LINES = [
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
]
MEOWS = ["mňau", "mrrrp", "mňaaau", "prrr", "mrr?"]
HAIRBALL_SAYS = ["hrk... hrk...", "ehm. moment", "nekoukej na mě"]
BUTT_SAYS = ["tohle je pro tebe", "*ocas nahoru*", "koukej", "tak co"]
BACK_SAYS = ["a jsi zpátky", "kde jsi byla?", "hlídala jsem ti to", "*protahuje se*"]

# what she coaches you through while the countdown runs
PAUSE_COACH = [
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
]
END_COACH = [
    "zavři to. zítra to tam bude pořád",
    "co nestihneš dneska, uteče pomalu jako stará myš",
    "šichta končí. jdi si lehnout do krabice",
    "hotovo je líp než dokonalé. ptej se koček",
    "postav se. dneska už na tu židli nesedej",
    "protáhni se naposled a jdi pryč od stolu",
    "dobrá práce. teď ji nech být",
]

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


_LII = _LASTINPUTINFO()
_LII.cbSize = ctypes.sizeof(_LII)


def _win32():
    try:
        return ctypes.windll.user32, ctypes.windll.kernel32
    except AttributeError:
        return None, None                      # not Windows


def idle_seconds():
    """Seconds since you last touched the keyboard or mouse. 0 where we can't tell."""
    user32, kernel32 = _win32()
    if not user32 or not user32.GetLastInputInfo(ctypes.byref(_LII)):
        return 0.0
    # GetTickCount wraps every 49 days, so subtract inside 32 bits or she thinks you left
    return ((kernel32.GetTickCount() - _LII.dwTime) % (2 ** 32)) / 1000.0


def sharing_screen():
    """True when the front window covers the whole screen: a call, a slideshow, a video."""
    user32, _ = _win32()
    if not user32:
        return False
    hwnd = user32.GetForegroundWindow()
    if not hwnd or hwnd in (user32.GetShellWindow(), user32.GetDesktopWindow()):
        return False
    if user32.GetWindowLongW(hwnd, -16) & 0x00C00000:   # GWL_STYLE & WS_CAPTION
        return False       # it still has a title bar, so it's only maximised, not fullscreen
    rect = _RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False
    return (rect.right - rect.left >= user32.GetSystemMetrics(0)
            and rect.bottom - rect.top >= user32.GetSystemMetrics(1))


# --------------------------------------------------------------------------- behaviour

class Pet:
    """Position + behaviour. No tkinter in here, so it can be tested headless."""

    def __init__(self, screen_w, x=None):
        self.screen_w = screen_w
        self.x = screen_w // 2 if x is None else x
        self.dir = 1
        self.state = "idle"
        self.until = 0.0
        self.say = ""
        self.say_until = 0.0
        self.extra = []      # lines run() wants her to say today, on top of LINES
        self.next_line = time.time() + random.uniform(*LINE_EVERY)
        self.worked = 0.0    # seconds of real work since her last break
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

    @property
    def max_x(self):
        return max(0, self.screen_w - W)

    def asleep(self, hour):
        return hour >= NIGHT[0] or hour < NIGHT[1]

    def speak(self, text, now, secs=4):
        self.say, self.say_until = text, now + secs

    def do(self, state, now, secs=None):
        self.state = state
        self.started = now
        self.until = now + (secs if secs else random.uniform(*DURATION.get(state, (2.5, 6))))

    def start_pause(self, now, kind="break"):
        span = PAUSE_SECS if kind == "break" else END_SECS
        prompts = PAUSE_COACH if kind == "break" else END_COACH
        self.state, self.dir, self.say, self.kind = "pause", 1, "", kind
        self.pause_until, self.pause_span = now + span, float(span)
        self.worked = 0.0
        self.coach = random.sample(prompts, k=min(len(prompts), max(1, span // COACH_EVERY)))

    def pause_left(self, now):
        return max(0, math.ceil(self.pause_until - now))

    def coach_line(self, now):
        """The stretch she's asking for right now; a new one every COACH_EVERY seconds."""
        if not self.coach:
            return ""
        done = self.pause_span - max(0.0, self.pause_until - now)
        return self.coach[min(len(self.coach) - 1, int(done // COACH_EVERY))]

    def zoom(self, now):
        """1.0 normally; eases up to PAUSE_ZOOM for a break and back down at the end."""
        if self.state != "pause":
            return 1.0
        left = max(0.0, self.pause_until - now)
        eased = min(1.0, (self.pause_span - left) / 0.5, left / 0.5)
        return 1.0 + (PAUSE_ZOOM - 1.0) * eased

    def _breathe(self, now):
        """4-7-8: her whole body does it so you can follow the cat instead of the text."""
        cycle = (now - (self.pause_until - self.pause_span)) % 19.0
        if cycle < 4:
            self.breath, self.breath_word = cycle / 4.0, "nádech"
        elif cycle < 11:
            self.breath, self.breath_word = 1.0, "zadrž"
        else:
            self.breath, self.breath_word = 1.0 - (cycle - 11) / 8.0, "výdech"

    def step(self, now, hour, away=False):
        dt = min(2.0, max(0.0, now - self.last_step)) if self.last_step else 0.0
        self.last_step = now
        if self.say and now > self.say_until:
            self.say = ""

        if self.state == "pause":
            self._breathe(now)
            if now >= self.pause_until:
                self.breath = 0.0
                if self.kind == "end":
                    self.do("rest", now, 90)   # shift's over, she lies down with you
                else:
                    self.state, self.until = "idle", 0.0
            return self.state

        if self.asleep(hour):
            self.state = "sleep"
            # keep sliding the timer, or she'd blurt a pep talk the second she wakes up
            self.next_line = now + random.uniform(*LINE_EVERY)
            return self.state
        if away:
            self.state = "away"                # nobody to talk to, so she naps instead
            self.next_line = now + random.uniform(*LINE_EVERY)
            return self.state
        if self.state in ("sleep", "away"):
            if self.state == "away":
                self.do("idle", now, 3)        # a beat to notice you, before anything else
                self.speak(random.choice(BACK_SAYS), now, 5)
            else:
                self.state, self.until = "idle", 0.0

        self.worked += dt                      # only counts while you are actually here
        if self.worked >= PAUSE_EVERY:
            self.start_pause(now)
            return self.state
        if now >= self.next_line:
            self.speak(random.choice(LINES + self.extra), now, 7)
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
                self.speak(random.choice(MEOWS), now, 2.5)
            elif self.state == "hairball":
                self.speak(random.choice(HAIRBALL_SAYS), now, 3)
            elif self.state == "butt":
                self.speak(random.choice(BUTT_SAYS), now, 3)
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


def draw_bubble(c, pet, hy):
    """Sized to the wrapped text and anchored above her head, never mirrored."""
    if not pet.say:
        return
    said = c.create_text(W // 2, hy - 42, text=pet.say, width=W - 30, anchor="s",
                         justify="center", fill=INK, font=("Segoe UI", 9, "bold"))
    x1, y1, x2, y2 = c.bbox(said)
    for dx, dy, r in ((16, 10, 5), (26, 20, 3)):
        c.create_oval(W // 2 + dx, y2 + dy, W // 2 + dx + r * 2, y2 + dy + r * 2,
                      fill="white", outline=DARK, width=2)
    box = c.create_rectangle(x1 - 10, y1 - 7, x2 + 10, y2 + 7,
                             fill="white", outline=DARK, width=2)
    c.tag_lower(box, said)


def draw_rear(c, pet, frame):
    """She turns her back on you. What you get is a spinning star where her tail starts."""
    cx, ay = W // 2, GROUND - WHEEL_R
    top, bottom = GROUND - 96, GROUND - 14

    if pet.cart:
        for wx in (cx - 54, cx + 54):
            c.create_oval(wx - WHEEL_R, ay - WHEEL_R, wx + WHEEL_R, ay + WHEEL_R,
                          fill=TIRE, outline="")
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
        c.create_line(lx, bottom - 12, lx, GROUND, width=10, fill=DARK, capstyle="round")

    sway = math.sin(frame * 0.11) * 9          # tail straight up, the way they do it
    c.create_line(cx + 2, top + 26, cx + 8 + sway * 0.4, top - 14,
                  cx + 10 + sway, top - 44,
                  width=9, fill=FUR, capstyle="round", smooth=True)

    c.create_oval(cx - 26, top - 30, cx + 26, top + 18, fill=FUR, outline="")   # back of head
    for ex, tilt in ((cx - 17, -9), (cx + 17, 9)):
        c.create_polygon(ex - 9, top - 20, ex + tilt, top - 44, ex + 9, top - 18,
                         fill=FUR, outline="")
    c.create_oval(cx - 44, top, cx + 44, bottom, fill=FUR, outline="")          # the rump
    for sx in (-22, 0, 22):                                                     # stripes
        c.create_line(cx + sx, top + 10, cx + sx, top + 30, width=4, fill=DARK, capstyle="round")

    # a pale patch so the star reads on any coat, then the star
    cy = (top + bottom) / 2 + 12
    c.create_oval(cx - 26, cy - 26, cx + 26, cy + 26, fill="#fdf6ec", outline="")
    starburst(c, cx, cy, 22, frame * 0.05)


def draw(c, pet, frame):
    c.delete("all")
    st = pet.state
    if st == "butt":
        draw_rear(c, pet, frame)
        draw_bubble(c, pet, GROUND - 120)
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
         width=9, fill=FUR, capstyle="round", smooth=True)

    # wheels, drawn behind the body so the haunch overlaps their inner edge
    if pet.cart:
        for cx, cy, r, tire in ((ax + 13, ay - 9, WHEEL_R - 4, "#2b2b30"),   # far wheel
                                (ax, ay, WHEEL_R, TIRE)):                    # near wheel
            oval(cx - r, cy - r, cx + r, cy + r, fill=tire, outline="")
            oval(cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5, fill=RIM, outline="")
            for k in range(3):
                a = pet.roll / WHEEL_R + k * math.pi / 3
                dx, dy = math.cos(a) * (r - 6), math.sin(a) * (r - 6)
                line([(cx - dx, cy - dy), (cx + dx, cy + dy)], width=2, fill=FRAME)
            oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=FRAME, outline="")
        line([(50, ay - 4), (82, ay - 12)], width=5, fill=STRAP, capstyle="round")  # sling

    # bowl of milk, set down right under her nose
    if st == "milk":
        oval(130, GROUND - 18, 176, GROUND - 2, fill=BOWL, outline=FRAME, width=2)
        oval(135, GROUND - 16, 171, GROUND - 8, fill=MILK, outline="")

    # a tuft of grass to chew on, and the hairball it leads to
    if st == "grass":
        for gx, gh, bend in ((132, 30, 7), (141, 42, -6), (150, 36, 9), (159, 26, -5)):
            line([(gx, GROUND - 2), (gx + bend, GROUND - gh)],
                 width=4, fill=GRASS, capstyle="round", smooth=True)
    elif st == "hairball" and pet.progress > 0.6:
        oval(158, GROUND - 13, 186, GROUND - 2, fill=DARK, outline="")
        oval(163, GROUND - 14, 179, GROUND - 6, fill=FUR, outline="")

    # legs (front pair sits wide apart so they don't collapse into one stub)
    if not lie:
        sw = math.sin(t * 2.2) * 7 if st == "walk" else 0
        for i, (lx, ph) in enumerate(((76, 1), (88, -1), (110, -1), (128, 1))):
            if i < 2:                                           # rear pair
                if in_cart:                                     # slung, never reaches the floor
                    line([(lx - 4, by + 12), (lx - 20, ay - 2)],
                         width=9, fill=DARK, capstyle="round")
                    continue
                if sit:
                    continue                                    # folded under when sitting
            if i == 3 and st == "lick":
                continue                                        # drawn last, over her head
            tipx, tipy = lx + (sw * ph if st == "walk" else 0), GROUND
            if i == 3 and st in ("highfive", "pause"):
                tipx, tipy = lx + 18, by - 20                   # paw up
            line([(lx, by + 14), (tipx, tipy)], width=10, fill=DARK, capstyle="round")

    # body + stripes
    oval(55 + bx - puff, by - 24 - puff, 136 + bx + puff, by + 22 + puff, fill=FUR, outline="")
    for sx in (80, 96, 112):
        line([(sx + bx, by - 21), (sx - 7 + bx, by - 4)], width=4, fill=DARK, capstyle="round")

    # cart frame, drawn over the body: upright at the hips, rail along the back, chest strap
    if pet.cart:
        line([(ax + 6, ay - 4), (54, cby - 30), (102, cby - 28), (106, cby + 4)],
             width=5, fill=FRAME, capstyle="round", joinstyle="round")
        if in_cart:
            line([(104, by - 27), (104, by + 21)], width=5, fill=STRAP)

    # ears, head
    poly([(hx - 21, hy - 12), (hx - 25, hy - 36), (hx - 5, hy - 22)], fill=FUR, outline="")
    poly([(hx + 13, hy - 20), (hx + 20, hy - 38), (hx + 26, hy - 15)], fill=FUR, outline="")
    oval(hx - 24, hy - 22, hx + 24, hy + 22, fill=FUR, outline="")

    # eyes (shut when she naps, and when she grooms, like the real thing)
    ey = hy - 2
    if napping or st == "lick":
        for ex in (hx - 9, hx + 9):
            line([(ex - 6, ey), (ex, ey + 4), (ex + 6, ey)],
                 width=2, fill=EYE, smooth=True, capstyle="round")
    else:
        blink = frame % 90 < 4
        for ex in (hx - 9, hx + 9):
            if blink:
                line([(ex - 6, ey), (ex + 6, ey)], width=2, fill=EYE, capstyle="round")
            else:
                oval(ex - 5, ey - 7, ex + 5, ey + 7, fill=EYE, outline="")
                oval(ex - 3, ey - 6, ex, ey - 3, fill="white", outline="")

    # nose, mouth, whiskers
    poly([(hx + 1, ey + 10), (hx + 11, ey + 10), (hx + 6, ey + 16)], fill=PINK, outline="")
    if st in ("meow", "hairball"):
        oval(hx + 1, ey + 15, hx + 13, ey + 26, fill=MOUTH, outline="")
        oval(hx + 4, ey + 21, hx + 11, ey + 26, fill=PINK, outline="")
    elif st in ("lick", "milk", "grass"):
        oval(hx + 2, ey + 14, hx + 13, ey + 23, fill=PINK, outline="")      # tongue out
    for wy in (ey + 8, ey + 14):
        line([(hx + 13, wy), (hx + 32, wy - 3)], width=1, fill=DARK)

    # the paw she's grooming, drawn last so it sits over her muzzle instead of behind it
    if st == "lick":
        line([(126, by + 14), (hx + 7, ey + 17)], width=10, fill=DARK, capstyle="round")
        oval(hx - 1, ey + 9, hx + 17, ey + 25, fill=DARK, outline="")
        oval(hx + 3, ey + 12, hx + 9, ey + 17, fill=PINK, outline="")       # toe bean

    if napping:
        for i, s in enumerate("zZz"):
            c.create_text(fx(hx + 20 + i * 13), hy - 32 - i * 13 - (frame // 6) % 7,
                          text=s, fill="#7fb2e0", font=("Segoe UI", 9 + i * 3, "bold"))

    draw_bubble(c, pet, hy)


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
    """The sign she holds up during a break, drawn at final size after the zoom."""
    end = pet.kind == "end"
    seconds_left = pet.pause_left(now)
    s = k / PAUSE_ZOOM                         # grows with her instead of popping in full size
    cx, top = cw / 2, 16 * s
    c.create_rectangle(cx - 140 * s, top, cx + 140 * s, top + 200 * s,
                       fill="white", outline=STRAP, width=6 * s)
    c.create_text(cx, top + 34 * s, text="ŠICHTA KONČÍ" if end else "STOP", fill=STRAP,
                  font=("Segoe UI", max(8, int((19 if end else 26) * s)), "bold"))
    c.create_text(cx, top + 68 * s, text="hotovo. zavři to" if end else "teď pauzička",
                  fill=INK, font=("Segoe UI", max(6, int(14 * s)), "bold"))
    c.create_text(cx, top + 104 * s, text="%d s  ·  %s" % (seconds_left, pet.breath_word),
                  fill=MUTED, font=("Segoe UI", max(6, int(19 * s)), "bold"))
    c.create_line(cx - 108 * s, top + 130 * s, cx + 108 * s, top + 130 * s,
                  fill="#e4ded4", width=2 * s)
    c.create_text(cx, top + 164 * s, text=pet.coach_line(now), fill=INK, width=248 * s,
                  justify="center", font=("Segoe UI", max(6, int(12 * s))))


# --------------------------------------------------------------------------- her memory

def set_fur(palette):
    global FUR, DARK, PINK
    FUR, DARK, PINK = PALETTES.get(palette, PALETTES["zrzava"])


def load_config(path=CONFIG):
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
        return cfg if isinstance(cfg, dict) else {}
    except (OSError, ValueError):
        return {}                              # missing or corrupt: she just asks again


def save_config(cfg, path=CONFIG):
    try:
        path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass                                   # read-only folder: she forgets, but still runs


def czech_days(n):
    return "%d %s" % (n, "den" if n == 1 else "dny" if n < 5 else "dní")


def greeting(cfg, today):
    """Day one she introduces herself; after that she picks up where she left off."""
    name = cfg.get("name") or FALLBACK_NAME
    first, last = cfg.get("first_seen"), cfg.get("last_seen")
    if not first or first == today:
        return "ahoj, jsem %s" % name
    days = (date.fromisoformat(today) - date.fromisoformat(first)).days + 1
    gap = (date.fromisoformat(today) - date.fromisoformat(last)).days if last else 0
    if gap >= 2:
        return "chyběla jsi mi! %s jsme se neviděly" % czech_days(gap)
    return "zase já. jsme spolu %d. den" % days


def water_line(cfg, today, hour):
    """Her afternoon nag about drinking, or nothing if it isn't warranted."""
    w = cfg.get("water") or {}
    drunk = w.get("count", 0) if w.get("date") == today else 0
    if hour < 14 or drunk >= WATER_GOAL:
        return None
    if drunk == 0:
        return "dneska ses ještě nenapila. ani jednou. koukám"
    return "dneska jsme to daly %d×. na kočku dobrý, na člověka málo" % drunk


# --------------------------------------------------------------------------- windows

def welcome(root, cfg=None):
    """Pick a colour and a name, with her rolling along live underneath. Returns the config."""
    import tkinter as tk

    cfg = dict(cfg or {})
    chosen = {"name": cfg.get("name", ""), "fur": cfg.get("fur", "zrzava"),
              "cart": cfg.get("cart", True)}
    win = tk.Toplevel(root)
    win.title("Vítej!")
    win.resizable(False, False)
    win.configure(bg=PAPER)

    tk.Label(win, text="Máš novou kočku.", bg=PAPER, fg=INK,
             font=("Segoe UI", 15, "bold")).pack(pady=(18, 0))
    tk.Label(win, text="Vyber jí barvu a dej jí jméno.", bg=PAPER, fg=MUTED,
             font=("Segoe UI", 10)).pack(pady=(2, 4))

    preview = tk.Canvas(win, width=W, height=H, bg=PAPER, highlightthickness=0)
    preview.pack()
    demo = Pet(1000)
    demo.state = "walk"
    anim = {"frame": 0}

    def spin():
        if not win.winfo_exists():
            return
        demo.roll += SPEED
        anim["frame"] += 1
        draw(preview, demo, anim["frame"])
        win.after(TICK, spin)

    fur_var = tk.StringVar(value=chosen["fur"])
    row = tk.Frame(win, bg=PAPER)
    row.pack(pady=(0, 10))
    for key, label in PALETTE_LABELS:
        tk.Radiobutton(row, text=label, value=key, variable=fur_var, bg=PAPER, fg=INK,
                       activebackground=PAPER, selectcolor="white", font=("Segoe UI", 10),
                       command=lambda: set_fur(fur_var.get())).pack(side="left", padx=4)

    tk.Label(win, text="Jak se bude jmenovat?", bg=PAPER, fg=INK,
             font=("Segoe UI", 10)).pack()
    entry = tk.Entry(win, font=("Segoe UI", 12), justify="center", width=18)
    entry.insert(0, chosen["name"])
    entry.pack(pady=(4, 12))
    entry.focus_set()

    def done(*_):
        chosen["name"] = entry.get().strip()[:14] or FALLBACK_NAME
        chosen["fur"] = fur_var.get()
        win.destroy()

    tk.Button(win, text="Pojď ke mně!", font=("Segoe UI", 11, "bold"), bg="#e8a75c",
              activebackground="#d99546", relief="flat", padx=18, pady=6,
              command=done).pack(pady=(0, 18))
    win.bind("<Return>", done)
    win.protocol("WM_DELETE_WINDOW", done)

    set_fur(chosen["fur"])
    spin()
    win.update_idletasks()
    win.geometry("+%d+%d" % ((win.winfo_screenwidth() - win.winfo_width()) // 2,
                             (win.winfo_screenheight() - win.winfo_height()) // 3))
    win.grab_set()
    root.wait_window(win)
    set_fur(chosen["fur"])
    return chosen


def ask_focus(root, today, hour):
    """Once a day she asks for the one thing that matters. Empty answer is a fine answer."""
    if not 6 <= hour < WORK_END:
        return None                            # too late to promise anything
    from tkinter import simpledialog
    got = simpledialog.askstring(
        "Jedna věc", "Co je dneska ta jedna věc, kterou chceš mít hotovou?", parent=root)
    return {"date": today, "text": (got or "").strip()[:60], "done": False}


def run():
    import tkinter as tk

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    try:
        root.attributes("-transparentcolor", KEY)
    except tk.TclError:
        pass                                   # non-Windows: she gets a solid backdrop
    root.configure(bg=KEY)

    root.withdraw()                            # ask before she shows up, not over her
    cfg = load_config()
    if not cfg.get("name"):                    # only ever asked once, on the very first run
        cfg = welcome(root, cfg)
    set_fur(cfg.get("fur", "zrzava"))

    day = {"date": date.today().isoformat()}
    hello = greeting(cfg, day["date"])
    cfg.setdefault("first_seen", day["date"])
    cfg["last_seen"] = day["date"]
    if (cfg.get("focus") or {}).get("date") != day["date"]:
        asked = ask_focus(root, day["date"], datetime.now().hour)
        if asked:
            cfg["focus"] = asked
    save_config(cfg)
    root.deiconify()

    pet = Pet(root.winfo_screenwidth())
    pet.cart = cfg.get("cart", True)
    pet.speak(hello, time.time(), 6)
    if "--demo" in sys.argv:                   # so you don't have to wait an hour to see it
        pet.next_line, pet.worked = time.time() + 3, PAUSE_EVERY - 12
    c = tk.Canvas(root, width=W, height=H, bg=KEY, highlightthickness=0)
    c.pack()
    ui = {"frame": 0, "drag": None, "moved": 0, "away": False, "hidden": False}

    def focus_label():
        f = cfg.get("focus") or {}
        if not f.get("text"):
            return "dnes: (nic)"
        return ("hotovo: " if f.get("done") else "dnes: ") + f["text"]

    def toggle_focus():
        f = cfg.get("focus") or {}
        if not f.get("text"):
            return
        f["done"] = not f.get("done")
        cfg["focus"] = f
        save_config(cfg)
        menu.entryconfigure(focus_at, label=focus_label())
        pet.speak("jsem na tebe pyšná" if f["done"] else "tak jo, jedem dál", time.time(), 5)

    def drank():
        w = cfg.get("water") or {}
        if w.get("date") != day["date"]:
            w = {"date": day["date"], "count": 0}
        w["count"] += 1
        cfg["water"] = w
        save_config(cfg)
        left = WATER_GOAL - w["count"]
        pet.speak("%d. dneska. ještě %d" % (w["count"], left) if left > 0
                  else "%d. a to je ono" % w["count"], time.time(), 5)

    def press(e):
        ui["drag"], ui["moved"] = e.x_root, 0

    def motion(e):
        if ui["drag"] is None:
            return
        d = e.x_root - ui["drag"]
        ui["moved"] += abs(d)
        pet.x = min(pet.max_x, max(0, pet.x + d))
        ui["drag"] = e.x_root

    def release(e):
        if ui["moved"] >= 5 or pet.state == "pause":
            ui["drag"] = None
            return                             # that was a drag, or she's holding the sign
        now = time.time()
        if pet.state == "milk" and 130 <= e.x <= 176 and e.y >= GROUND - 20:
            drank()                            # you clinked her bowl, so you drank too
        else:
            pet.do("highfive", now, 3)
            pet.speak(random.choice(LINES + pet.extra), now, 7)
        ui["drag"] = None

    cart_var = tk.BooleanVar(value=pet.cart)

    def toggle_cart():
        pet.cart = cart_var.get()
        if pet.cart and pet.state == "sit":
            pet.do("idle", time.time(), 2)
        cfg["cart"] = pet.cart
        save_config(cfg)

    def rename():
        cfg.update(welcome(root, cfg))
        save_config(cfg)
        menu.entryconfigure(0, label=cfg["name"])
        pet.speak("teď jsem %s" % cfg["name"], time.time(), 5)

    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label=cfg["name"], state="disabled")
    menu.add_command(label=focus_label(), command=toggle_focus)
    focus_at = 1
    menu.add_separator()
    menu.add_command(label="pojď sem", command=lambda: pet.do("walk", time.time(), 4))
    menu.add_command(label="dej packu", command=lambda: pet.do("highfive", time.time(), 4))
    menu.add_command(label="mlíčko", command=lambda: pet.do("milk", time.time()))
    menu.add_command(label="napila jsem se", command=drank)
    menu.add_command(label="řekni něco",
                     command=lambda: pet.speak(random.choice(LINES + pet.extra),
                                               time.time(), 7))
    menu.add_command(label="dáme pauzu", command=lambda: pet.start_pause(time.time()))
    menu.add_separator()
    menu.add_checkbutton(label="vozíček", variable=cart_var, command=toggle_cart)
    menu.add_command(label="přejmenovat / barva", command=rename)
    menu.add_command(label="zavřít", command=root.destroy)

    c.bind("<ButtonPress-1>", press)
    c.bind("<B1-Motion>", motion)
    c.bind("<ButtonRelease-1>", release)
    c.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def slow_checks(now, hour):
        """The expensive Windows questions, asked once a second instead of 25 times."""
        ui["away"] = idle_seconds() > AWAY_AFTER
        today = date.today().isoformat()
        if today != day["date"]:               # she ran past midnight
            day["date"] = today
            cfg["last_seen"] = today
            save_config(cfg)
        pet.extra = [w for w in (water_line(cfg, today, hour),) if w]
        if (cfg.get("ended") != today and hour >= WORK_END and not pet.asleep(hour)
                and not ui["away"] and pet.state != "pause"):
            cfg["ended"] = today
            save_config(cfg)
            pet.start_pause(now, "end")

    def tick():
        now = time.time()
        hour = datetime.now().hour
        if ui["frame"] % SLOW == 0:
            slow_checks(now, hour)
            hide = sharing_screen()            # a call or a slideshow: she gets out of the way
            if hide != ui["hidden"]:
                (root.withdraw if hide else root.deiconify)()
                ui["hidden"] = hide
        ui["frame"] += 1
        if ui["hidden"]:
            root.after(TICK * 5, tick)
            return

        pet.screen_w = root.winfo_screenwidth()   # survives docking / a resolution change
        pet.x = min(pet.x, pet.max_x)
        pet.step(now, hour, ui["away"])

        k = pet.zoom(now)
        extra = PAUSE_EXTRA if pet.state == "pause" else 0   # headroom for the sign
        cw, ch = int(W * k), int((H + extra) * k)
        c.config(width=cw, height=ch)
        draw(c, pet, ui["frame"])
        zoom_canvas(c, k)
        if extra:
            c.move("all", 0, extra * k)           # push her down, sign goes in above her
            draw_sign(c, cw, k, pet, now)

        wx = int(pet.x - (cw - W) / 2)            # grow around her, not off to one side
        wx = min(max(0, wx), max(0, root.winfo_screenwidth() - cw))
        top = root.winfo_screenheight() - TASKBAR - int((GROUND + extra) * k)
        root.geometry("%dx%d+%d+%d" % (cw, ch, wx, top))
        root.after(TICK, tick)

    tick()
    root.mainloop()


# --------------------------------------------------------------------------- self-check

def selftest():
    now = time.time()
    p = Pet(1920, x=0)
    assert p.cart, "she comes in her cart by default"
    assert p.asleep(23) and p.asleep(3) and not p.asleep(12)
    assert p.max_x == 1920 - W

    p.do("walk", now, 999)
    p.dir = -1
    for i in range(4000):                       # bounces off both edges, never escapes
        p.step(now + i * 0.04, 12)
        assert 0 <= p.x <= p.max_x, p.x

    now += 200
    assert p.step(now, 23) == "sleep"           # night wins over whatever she was doing
    assert p.step(now, 12) != "sleep"           # and she wakes up again

    # she stops talking and stops counting your hours the moment you leave the desk
    p.worked, p.say = 0.0, ""
    assert p.step(now + 1, 12, away=True) == "away"
    assert not p.say and p.worked == 0.0, "no pep talks into an empty room"
    p.step(now + 2, 12)
    assert p.say in BACK_SAYS, "she notices you came back"

    p.next_line, p.say = now - 1, ""
    p.step(now, 23)
    assert not p.say and p.next_line > now, "silent at night, and no blurting on waking"
    p.state, p.until, p.next_line = "idle", now + 9999, now - 1   # no trick picked over it
    p.step(now, 12)
    assert p.say in LINES and p.next_line > now

    p.speak("ahoj", now, 1)
    p.step(now + 2, 12)
    assert p.say == "", "speech bubble expires"

    # rolling on a smaller screen than she started on (docking, resolution change)
    p.screen_w = 400
    p.do("walk", now, 999)
    for i in range(200):
        p.step(now + i * 0.04, 12)
        assert 0 <= p.x <= p.max_x, p.x

    # the cart
    before = p.roll
    p.do("walk", now, 999)
    p.step(now, 12)
    assert p.roll > before, "wheels turn while she rolls"
    p.do("idle", now, 999)
    held = p.roll
    p.step(now, 12)
    assert p.roll == held, "wheels stop when she stops"
    seen = set()
    for _ in range(800):
        p.until, p.worked = 0.0, 0.0            # force a fresh trick every step
        seen.add(p.step(now, 12))
    assert "sit" not in seen, "no sitting while in the cart"
    assert {"lick", "meow", "milk", "grass", "rest", "butt"} <= seen, "all her little things"

    # grass goes down and fur comes up: hairballs follow grass, never out of nowhere
    for _ in range(40):
        p.do("grass", now, 1)
        p.until, p.worked = 0.0, 0.0
        if p.step(now, 12) == "hairball":
            break
    else:
        raise AssertionError("grass never once led to a hairball")

    # the hourly break is an hour of WORK, not an hour on the clock
    p = Pet(1920, x=500)
    p.last_step = now
    p.step(now + PAUSE_EVERY / 2, 12)
    assert p.state != "pause", "half an hour in, no break yet"
    for i in range(int(PAUSE_EVERY)):           # the rest of the hour, one second at a time
        if p.step(now + PAUSE_EVERY / 2 + i, 12) == "pause":
            break
    assert p.state == "pause", "an hour of work earns a break"
    started = p.pause_until - PAUSE_SECS
    assert p.pause_left(started) == PAUSE_SECS and not p.say, "the sign replaces the bubble"
    assert p.worked == 0.0, "the hour resets"
    assert p.zoom(started) == 1.0 and p.zoom(started + 1) == PAUSE_ZOOM, "eases up, no popping"
    assert 1.0 < p.zoom(p.pause_until - 0.25) < PAUSE_ZOOM, "and eases back down"
    coached = {p.coach_line(started + s) for s in range(0, PAUSE_SECS, 2)}
    assert len(coached) == PAUSE_SECS // COACH_EVERY, "a new stretch every few seconds"
    assert coached <= set(PAUSE_COACH) and "" not in coached
    parked = p.x
    p.step(started + 2, 12)
    assert p.state == "pause" and p.x == parked, "frozen in place while the sign is up"
    assert p.breath_word == "nádech" and 0 < p.breath <= 1, "4-7-8 while she holds the sign"
    p.step(started + 7, 12)
    assert p.breath_word == "zadrž" and p.breath == 1.0
    p.step(started + 15, 12)
    assert p.breath_word == "výdech" and p.breath < 1.0
    assert p.step(p.pause_until, 12) != "pause" and p.zoom(p.pause_until) == 1.0

    # the end of the day is a longer sign and she lies down afterwards
    p.start_pause(now, "end")
    assert p.kind == "end" and p.pause_left(now) == END_SECS
    assert p.coach_line(now) in END_COACH
    p.step(now + END_SECS, 12)
    assert p.state == "rest", "shift's over, she lies down"

    p.worked = PAUSE_EVERY
    p.step(now, 23)
    assert p.state == "sleep", "no breaks in the middle of the night"

    # what she says
    assert all(len(s) <= 70 for s in LINES), "longer lines overflow the bubble"
    assert len(LINES) >= 20, "fewer than this and she repeats herself the first day"
    assert all(len(s) <= 60 for s in PAUSE_COACH + END_COACH), "longer prompts overflow the sign"

    # drinking: she only nags in the afternoon, and stops once you've had enough
    today = "2026-09-18"
    assert water_line({}, today, 9) is None, "no nagging before the afternoon"
    assert "ani jednou" in water_line({}, today, 15)
    assert "3×" in water_line({"water": {"date": today, "count": 3}}, today, 15)
    assert water_line({"water": {"date": today, "count": WATER_GOAL}}, today, 15) is None
    assert water_line({"water": {"date": "2026-09-17", "count": 9}}, today, 15) is not None

    # she picks up where she left off instead of starting over
    assert greeting({"name": "Claudie"}, today) == "ahoj, jsem Claudie"
    assert greeting({"name": "Claudie", "first_seen": today}, today) == "ahoj, jsem Claudie"
    assert "12. den" in greeting(
        {"name": "C", "first_seen": "2026-09-07", "last_seen": "2026-09-17"}, today)
    assert "3 dny" in greeting(
        {"name": "C", "first_seen": "2026-09-01", "last_seen": "2026-09-15"}, today)
    assert czech_days(1) == "1 den" and czech_days(4) == "4 dny" and czech_days(9) == "9 dní"

    # sensing the machine must never throw, whatever it answers
    assert idle_seconds() >= 0.0
    assert sharing_screen() in (True, False)

    # her memory: same name and colour after a restart
    assert all(len(v) == 3 for v in PALETTES.values()), "fur, shading, nose"
    assert {k for k, _ in PALETTE_LABELS} == set(PALETTES), "every palette is offered"
    tmp = CONFIG.with_name("_selftest.json")
    save_config({"name": "Micka", "fur": "seda", "cart": True}, tmp)
    assert load_config(tmp) == {"name": "Micka", "fur": "seda", "cart": True}
    tmp.write_text("{ rozbite", encoding="utf-8")
    assert load_config(tmp) == {}, "a corrupt config must not stop her"
    tmp.unlink()
    assert load_config(tmp) == {}, "a missing config must not stop her"
    set_fur("seda")
    assert FUR == PALETTES["seda"][0]
    set_fur("neexistuje")
    assert FUR == PALETTES["zrzava"][0], "unknown palette falls back"
    print("ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else run()

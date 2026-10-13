# Kočka na plochu

Kočička na vozíčku, která ti jezdí po spodku obrazovky a hlídá tě při práci.
Během dne se projíždí, olizuje se, mňouká, chodí se napít mlíčka a povídá ti povzbuzující
(a hodně kočičí) hlody. Jednou za hodinu **skutečné práce** tě zastaví, zvětší se, zvedne
ceduli STOP a odpočítá 30 vteřin, během kterých tě vede protahováním a dýcháním.
Odpoledne ti řekne, ať to zavřeš.

Nic neinstaluje, nic neposílá na internet, nic o tobě nesbírá. Je to jeden soubor,
který běží u tebe na počítači.

**Při prvním spuštění se tě zeptá, jakou má mít barvu a jak se bude jmenovat.** Pak už
se neptá nikdy, pamatuje si to a vrací se pořád stejná.

---

## Co k tomu potřebuješ

Jenom **Python**. Nic dalšího, žádné instalace balíčků.

- Napiš do vyhledávání ve Windows `Microsoft Store`, najdi **Python 3** a dej Získat.
- Nebo stáhni z [python.org/downloads](https://www.python.org/downloads/). Při instalaci
  zaškrtni **„Add python.exe to PATH"**, to je důležité.

Ověříš to tak, že v Příkazovém řádku napíšeš `python --version` a vypíše se ti číslo verze.

---

## Jak ji spustit

1. Udělej si někde složku, třeba `C:\kocka`.
2. Zkopíruj kód úplně dole a ulož ho do té složky jako **`kocicka.py`**
   (v Poznámkovém bloku: Soubor -> Uložit jako -> Typ souboru: **Všechny soubory**, jinak
   z toho udělá `kocicka.py.txt` a nepůjde to spustit).
3. Do stejné složky ulož druhý soubor jako **`kocicka.bat`** s tímhle obsahem:

   ```bat
   @echo off
   start "" pythonw "%~dp0kocicka.py"
   ```

4. Dvojklik na **`kocicka.bat`**.
5. Vyskočí uvítací okénko. Vybereš barvu, napíšeš jméno, dáš „Pojď ke mně!".
   Pak se tě ještě jednou denně zeptá, co je dneska ta jedna věc, kterou chceš stihnout.
   (Můžeš to nechat prázdné, nevadí.)

Do složky `%APPDATA%\kocicka` si uloží soubor `kocka.json`, kde si pamatuje jméno,
barvu, kolik jste spolu dní a kolikrát ses dneska napila. Nikam se neposílá. (Starší
verze ho měly vedle `kocicka.py`; při prvním spuštění si ho přenese sama a ten starý
můžeš smazat. Na Macu je v `~/Library/Application Support/kocicka`, na Linuxu
v `~/.config/kocicka`.)

Aby ti naskakovala sama po zapnutí počítače: stiskni **Win+R**, napiš `shell:startup`,
Enter, a do té složky hoď zástupce na `kocicka.bat` (pravý klik -> Kopírovat, pak
pravý klik ve složce -> Vložit zástupce).

---

## Co dělá

**Sama od sebe**

| | |
|---|---|
| **Jezdí** | projíždí se po spodku obrazovky, od krajů se odrazí a otočí |
| **Olizuje se** | zvedne packu k tlamičce a zavře oči, jak se to dělá |
| **Mňouká** | otevře pusinku a mňoukne |
| **Pije mlíčko** | postaví si před sebe misku a sehne se k ní |
| **Žere trávu** | a pak z toho většinou vyblije chlupy. Jak to u koček chodí |
| **Vyleze z vozíku** | občas si ho sundá a na chvíli si zdřímne vedle něj |
| **Otočí se k tobě zadkem** | protože je kočka. Co uvidíš, uvidíš |
| **Povídá** | každých pár minut jeden povzbuzující kočičí hlod |
| **Dýchá a mrká** | pořád, i když zrovna nic nedělá |
| **Večer usne** | od 22:00 do 7:00 svěsí hlavu, zavře oči a nad ní stoupá Zzz. Když pracuješ i v noci, počítá ti to dál a pauzu ti dá taky |

**Umí poznat, jestli jsi u počítače**

Když 5 minut nesáhneš na myš ani klávesnici, usne a přestane mluvit. Nemá smysl
ukazovat ceduli do prázdné místnosti. Až se vrátíš, protáhne se a všimne si tě.

Hodina do pauzy se jí kvůli tomu počítá jenom z **doby, kdy tam opravdu jsi**, ne
podle hodin na zdi. A když jsi byla pryč, bere to jako pauzu: hodina se počítá znovu
od nuly. Na Macu to pozná taky, na Linuxu jen s nainstalovaným `xprintidle`.
Když ji vypneš a zase pustíš, pamatuje si, kolik jsi toho dneska odpracovala.

**Když jde něco přes celou obrazovku, schová se**

Jakmile je vepředu okno přes celý monitor a bez titulku (prezentace, hovor nebo video
na celou obrazovku), zmizí. Když to skončí, vrátí se. Jestli sdílíš obrazovku, poznat
neumí: když sdílíš obyčejné okno nebo celou plochu, zůstane vidět. Čas schovaná ti
počítá dál jako práci, a když mezitím přijde čas na pauzu, počká, až zase vyleze.

**Jednou za hodinu práce: pauza**

Zvětší se na dvojnásobek, zvedne ceduli **STOP / teď pauzička** a spustí odpočet
30 vteřin. Během něj tě vede protahováním, každých pár vteřin novou větou
(„ramena dozadu a dolů", „koukni se z okna na něco daleko", „protáhni krk"...).
Zároveň se jí nafukuje a splaskává tělo v rytmu **4-7-8** (nádech 4 vteřiny, zadrž 7,
výdech 8) a na ceduli píše, ve které fázi jsi. Dýchej podle kočky, ne podle textu.
Když se to zrovna nehodí, pravý klik -> `přeskočit pauzu` nebo `pauzu až za 10 minut`.

**V 16:00 ti řekne, ať toho necháš**

Jednou denně udělá delší verzi téhle cedule: **ŠICHTA KONČÍ / hotovo. zavři to.**
Pak si lehne. Ukáže ji, jen když jsi ten den u počítače aspoň půl hodiny pracovala,
takže když ji pustíš až večer, nestraší. Kliknutím ceduli složí, přes pravý klik ji
odložíš o 10 minut. Kdyby ti to vycházelo blbě, změň nahoře v souboru `WORK_END = 16`.

**Hlídá ti pití**

V menu je `napila jsem se`. Nebo když zrovna pije mlíčko, klikni jí na misku, to je
totéž. Odpoledne ti řekne, jak na tom jste. Cíl je 6 skleniček, pak přestane rýpat.

**Jedna věc na dnešek**

Ráno se zeptá, co je dneska ta jedna věc. Máš ji pak nahoře v menu. Když ji máš
hotovou, klikni na ni a je z toho `hotovo:`. Zítra se zeptá znovu, i když ji necháš
běžet přes noc.

**Když na ni sáhneš**

| Akce | Co udělá |
|---|---|
| **Levý klik** | dá packu a něco ti řekne; na konci dne složí ceduli |
| **Tažení myší** | přesuneš ji po šířce obrazovky |
| **Pravý klik** | celé menu: dnešní věc, pojď sem, dej packu, mlíčko, napila jsem se, řekni něco, dáme pauzu, přeskočit pauzu, pauzu až za 10 minut, vozíček, přejmenovat / barva, zavřít |

---

## Když si to chceš rozmyslet

**Jiné jméno nebo barva** -> pravý klik -> `přejmenovat / barva`. Otevře se stejné okénko
jako na začátku. Když ho zavřeš křížkem, nic se nezmění.

**Úplně od nuly** -> smaž složku `%APPDATA%\kocicka` (napiš to do adresního řádku
Průzkumníka) a pusť ji znova. Zeptá se jako poprvé.

**Chodí po čtyřech místo vozíčku** -> pravý klik -> odškrtni `vozíček`.

**Nechci čekat hodinu, chci tu pauzu vidět teď** -> pravý klik -> `dáme pauzu`.
Nebo pusť `python kocicka.py --demo`, to zrychlí časovače.

---

## Kdyby něco nefungovalo

**Sedí na hlavním panelu nebo plave nad ním.** Na Windows se řídí tím, kde je panel,
takže by neměla. Na Macu a Linuxu otevři `kocicka.py` a nahoře změň číslo u
`TASKBAR = 40`. Větší číslo = výš.

**Zmizela a nevrací se.** Nejspíš je vepředu něco přes celou obrazovku. Přepni na
normální okno (ne přes celou obrazovku) a do vteřiny je zpátky.

**Je kolem ní světlý obdélník.** Průhlednost pozadí umí jenom Windows. Na Macu nebo
Linuxu bude mít kolem sebe krémový čtverec, jinak funguje stejně (jen se neschová
za aplikací přes celou obrazovku).

**Dvojklik na `kocicka.bat` jenom blikne a nic se nestane.** Nejspíš není Python v PATH.
Přeinstaluj ho a zaškrtni „Add python.exe to PATH".

**Chci ověřit, že je soubor v pořádku.** V Příkazovém řádku ve složce spusť
`python kocicka.py --selftest`. Když vypíše `ok`, je všechno jak má být.

**Nepamatuje si jméno.** Když jí nejde zapisovat do složky, jednou ti to řekne
v bublině. Zkontroluj, že máš do `%APPDATA%` právo zapisovat.

---

## Kód

Ulož jako `kocicka.py`:

```python
#!/usr/bin/env python3
"""Kocicka - a desktop cat in a wheelchair who keeps you company and looks after you.

stdlib only (tkinter + ctypes), no assets, no install, nothing leaves your machine.
On the first run she asks for a name and a colour; after that she remembers both in
her config file (see config_dir) and comes back the same cat. She notices when you step
away, gets out of the way of fullscreen apps, stops you for a stretch once an hour of
actual work, and calls it a day when the day is done.
  run:        python kocicka.py
  demo:       python kocicka.py --demo        (speeds the timers up so you see it now)
  self-check: python kocicka.py --selftest    (also runs tests/ when it sits next to her)
"""
from __future__ import annotations

import contextlib
import ctypes
import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime
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
NIGHT = (22, 7)           # dozes from 22:00 to 07:00: no pep talks, no end-of-day sign, but
                          # your work still counts and night owls still get their break

PALETTES = {         # fur, shading/legs, nose
    "zrzava": ("#e8a75c", "#b9702e", "#f2a0a8"),
    "seda": ("#a8b2c1", "#6f7d91", "#e0a3ad"),
    "smetanova": ("#f0dfc2", "#c9ab82", "#f2a0a8"),
    "cerna": ("#55555f", "#33333a", "#e6909c"),
}
DEFAULT_FUR = "zrzava"
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
        self.restore_work(now)

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

    # the day
    def worked_today(self) -> float:
        return self.pet.total - self.day_start

    def new_day(self, today: str, now: float) -> None:
        """Past midnight: yesterday's one thing is yesterday's, and she'll ask again."""
        self.today = today
        self.day_start = self.pet.total
        self.end_not_before = 0.0
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
        self.save(now)
        self.pet.speak(STRINGS["focus_proud" if f["done"] else "focus_undo"], now, 5)
        return True

    def drank(self, now: float) -> None:
        w = self.cfg.get("water")
        if not isinstance(w, dict) or w.get("date") != self.today:
            w = {"date": self.today, "count": 0}
        w["count"] = (w.get("count") if isinstance(w.get("count"), int) else 0) + 1
        self.cfg["water"] = w
        self.save(now)
        left = WATER_GOAL - w["count"]
        self.pet.speak(STRINGS["water_count"] % (w["count"], left) if left > 0
                       else STRINGS["water_done"] % w["count"], now, 5)

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
        if self.hidden:
            return False
        key = (self.frame(now), p.state, p.dir, p.cart, p.fur, round(p.x, 1), round(p.roll, 1),
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


if __name__ == "__main__":
    sys.exit(selftest()) if "--selftest" in sys.argv else run(sys.argv[1:])
```

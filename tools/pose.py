"""Renders every pose side by side for six seconds, so a drawing change can be checked
in one screenshot (that is how preview.png was made).   python tools/pose.py

With "break" it shows the hourly break instead, frozen mid-countdown with the sign up
(that is how break.png was made).                        python tools/pose.py break
"""
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kocicka as K

STATES = ["walk", "idle", "lick", "meow", "milk", "grass", "hairball", "rest",
          "away", "butt", "highfive", "sit", "sleep", "pause"]
PER_ROW = 7


def pose_sheet(root):
    for r in range(0, len(STATES), PER_ROW):
        row = tk.Frame(root, bg="white")
        row.pack()
        for st in STATES[r:r + PER_ROW]:
            cell = tk.Frame(row, bg="white")
            cell.pack(side="left")
            tk.Label(cell, text=st, bg="white", font=("Consolas", 10, "bold")).pack()
            c = tk.Canvas(cell, width=K.W, height=K.H, bg="white", highlightthickness=1)
            c.pack()
            pet = K.Pet(1000)
            pet.state = st
            pet.cart = st != "sit"
            pet.progress = 0.8
            pet.breath = 0.8
            pet.say = "koukat z okna je taky práce" if st == "idle" else ""
            K.draw(c, pet, 30)


def break_sign(root):
    """Exactly what render() draws during a break, 9 seconds in (second stretch, holding)."""
    pet = K.Pet(1000)
    pet.start_pause(0.0)
    now = 9.0
    pet.step(now, 12)
    k = pet.zoom(now)
    cw, ch = int(K.W * k), int((K.H + K.PAUSE_EXTRA) * k)
    c = tk.Canvas(root, width=cw, height=ch, bg="white", highlightthickness=0)
    c.pack()
    K.draw(c, pet, 30, k)
    c.move("all", 0, K.PAUSE_EXTRA * k)
    K.draw_sign(c, cw, k, pet, now)


root = tk.Tk()
root.title("pozy")
root.configure(bg="white")
root.attributes("-topmost", True)
root.geometry("+0+0")
(break_sign if "break" in sys.argv[1:] else pose_sheet)(root)
root.after(6000, root.destroy)
root.mainloop()

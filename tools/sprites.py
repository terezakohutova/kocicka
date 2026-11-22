"""Cuts the new look out of the ChatGPT sheets in art/ and writes it into kocicka.py.

    python tools/sprites.py

Needs Pillow (pip install pillow); the cat herself never does. Each sheet is a grid of poses
on flat green. Every pose is keyed out, scaled so her head is the same size on every sheet,
snapped to one shared palette (so kocicka.py can recolour her coat and cart by swapping
palette entries) and stored as zlib-packed palette indices between the SPRITES markers.
"""
import base64
import re
import zlib
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "art"
SCALE = 2          # stored at twice her on-screen size, for the break zoom and sharp displays
COLOURS = 32       # shared palette size
CLEAR = 255        # palette index meaning "see-through"

# sheet, columns, rows, cell names in reading order (None = skip), height of the first
# named pose in her own units, which sets the scale for the whole sheet
SHEETS = [
    ("sheet-cart.png", 4, 2, ["c_idle", "c_blink", "c_meow", "c_lick",
                              "c_milk", "c_hairball", "c_paw", "c_sleep"], 115),
    ("sheet-nocart.png", 3, 3, ["n_idle", "n_blink", "n_sit", "n_lick", "n_meow",
                                "n_milk", "n_hairball", "n_paw", "n_sleep"], 104),
    ("sheet-extra.png", 3, 1, ["c_back", "cart", None], 115),
    ("sheet-back.png", 1, 1, ["n_back"], 104),
]
# the first named pose of sheet-extra is the empty cart, but the scale should come from her
SCALE_FROM = {"sheet-extra.png": "c_back"}
ORDER = {"sheet-extra.png": ["cart", "c_back", None]}   # where they actually sit, left to right


def keyed(im):
    """RGBA with the green screen gone and the green spill pulled off the edges."""
    im = im.convert("RGB")
    px = im.load()
    w, h = im.size
    out = Image.new("RGBA", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if g - max(r, b) > 90:
                op[x, y] = (61, 32, 22, 0)        # outline brown, so edges blend dark
            else:
                op[x, y] = (r, min(g, max(r, b) + 10), b, 255)
    return out


def cells(path, cols, rows):
    im = keyed(Image.open(path))
    w, h = im.size
    for j in range(rows):
        for i in range(cols):
            cell = im.crop((i * w // cols, j * h // rows, (i + 1) * w // cols, (j + 1) * h // rows))
            alpha = cell.getchannel("A").filter(ImageFilter.MinFilter(5))   # specks out
            box = alpha.getbbox()
            yield cell.crop(box)


def ear_dip(alpha):
    """Where a bow or a hat goes: the lowest point of her outline between the two highest
    peaks of it (her ears), as (x, y) in the sprite."""
    w, h = alpha.size
    a = alpha.load()
    top = []
    for x in range(w):
        y = next((y for y in range(h) if a[x, y]), h)
        top.append(y)
    first = min(range(w), key=lambda x: top[x])
    gap = w // 8
    second = min((x for x in range(w) if abs(x - first) > gap), key=lambda x: top[x])
    lo, hi = sorted((first, second))
    x = max(range(lo, hi + 1), key=lambda x: top[x])
    return x, top[x]


def far(a, b, d):
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) > d * d


def main():
    sprites = {}
    for name, cols, rows, names, height in SHEETS:
        order = ORDER.get(name, names)
        cut = dict(zip(order, cells(ART / name, cols, rows), strict=True))
        ref = cut[SCALE_FROM.get(name, names[0])]
        k = height * SCALE / ref.height
        for pose in names:
            if pose is None:
                continue
            im = cut[pose]
            rgb = im.convert("RGB").filter(ImageFilter.MedianFilter(5))   # the JPEG grain out
            rgb.putalpha(im.getchannel("A"))
            im = rgb
            im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                           Image.LANCZOS)
            sprites[pose] = im

    # one palette for everything. Each pose names its 24 main colours with how much of
    # each it uses; then, most used first, a colour gets a slot only if nothing picked so
    # far is close to it. Otherwise the acres of ginger fur would take every slot in
    # slightly different shades and leave none for the cart's lilac and grey
    counts = {}
    for spr in sprites.values():
        q = spr.convert("RGB").quantize(24, method=Image.Quantize.MEDIANCUT,
                                        dither=Image.Dither.NONE)
        pal = q.getpalette()
        for i, a in zip(q.tobytes(), spr.getchannel("A").tobytes(), strict=True):
            if a > 127:
                c = tuple(pal[i * 3:i * 3 + 3])
                counts[c] = counts.get(c, 0) + 1
    ranked = sorted(counts, key=counts.get, reverse=True)
    near = 60
    while True:
        picked = []
        for c in ranked:
            if all(far(c, p, near) for p in picked):
                picked.append(c)
        if len(picked) >= COLOURS or near <= 4:
            break
        near -= 4
    picked = picked[:COLOURS]
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette([v for c in picked for v in c] + [0, 0, 0] * (256 - len(picked)))
    flat = pal_img.getpalette()[:len(picked) * 3]
    palette = ["#%02x%02x%02x" % tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]

    quoted = ['"%s"' % c for c in palette]
    lines = ["SPRITE_PALETTE = ("] + ["    " + ", ".join(quoted[i:i + 8]) + ","
                                     for i in range(0, len(quoted), 8)] + [")",
             "SPRITES = {   # name: (width, height, bow x, bow y, zlib'd palette indices)"]
    total = 0
    for pose, s in sprites.items():
        idx = s.convert("RGB").quantize(palette=pal_img, dither=Image.Dither.NONE)
        idx = idx.filter(ImageFilter.ModeFilter(3))    # stray single pixels out
        alpha = s.getchannel("A").point(lambda v: 255 * (v > 127))
        data = bytearray(idx.tobytes())
        for i, a in enumerate(alpha.tobytes()):
            if not a:
                data[i] = CLEAR
        packed = base64.b64encode(zlib.compress(bytes(data), 9)).decode()
        total += len(packed)
        bx, by = ear_dip(alpha)
        chunks = [packed[i:i + 84] for i in range(0, len(packed), 84)]
        lines.append('    "%s": (%d, %d, %d, %d,' % (pose, s.width, s.height, bx, by))
        lines.extend('        "%s"' % c for c in chunks[:-1])
        lines.append('        "%s"),' % chunks[-1])
    lines.append("}")
    block = "\n".join(lines)

    src = (ROOT / "kocicka.py").read_text(encoding="utf-8")
    start, end = "# --- sprites: generated by tools/sprites.py, do not edit by hand ---", \
        "# --- end of sprites ---"
    new = re.sub(re.escape(start) + r".*?" + re.escape(end),
                 lambda _: start + "\n" + block + "\n" + end, src, flags=re.S)
    if new == src and block not in src:
        raise SystemExit("sprite markers not found in kocicka.py")
    (ROOT / "kocicka.py").write_text(new, encoding="utf-8", newline="\n")
    print("%d sprites, %d colours, %d KB of base64" % (len(sprites), len(palette), total // 1024))


if __name__ == "__main__":
    main()

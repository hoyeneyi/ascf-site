#!/usr/bin/env python3
"""Share image (og.png), apple touch icon and SVG favicon.

og.png is what shows up when someone texts or posts the link — the single
biggest first impression the site makes outside a browser.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "assets", "img")
FONTS = "/home/claude/fonts"

INK = (7, 12, 13)
STOPS = [(0.00, (15, 155, 164)), (0.18, (47, 167, 156)), (0.40, (242, 106, 60)),
         (0.58, (245, 156, 34)), (0.78, (178, 206, 59)), (1.00, (253, 209, 10))]


def spectrum(t):
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        if a <= t <= b:
            k = (t - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3))
    return STOPS[-1][1]


def oswald(size, weight=700):
    f = ImageFont.truetype(os.path.join(FONTS, "Oswald.ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def poppins(size):
    return ImageFont.truetype(os.path.join(FONTS, "Poppins-Medium.ttf"), size)


def gradient_text(canvas, xy, text, font, tracking=0):
    """Draw text filled with the spectrum across its own width."""
    x0, y0 = xy
    # measure with tracking
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    asc, desc = font.getmetrics()
    h = asc + desc
    mask = Image.new("L", (int(total) + 4, h + 4), 0)
    md = ImageDraw.Draw(mask)
    x = 0
    for ch, w in zip(text, widths):
        md.text((x, 0), ch, font=font, fill=255)
        x += w + tracking
    grad = Image.new("RGB", mask.size)
    gd = ImageDraw.Draw(grad)
    for i in range(mask.size[0]):
        gd.line([(i, 0), (i, mask.size[1])], fill=spectrum(i / max(1, mask.size[0] - 1)))
    canvas.paste(grad, (int(x0), int(y0)), mask)
    return total


def tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x - xy[0] - tracking


def ribbon(canvas, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    band = Image.new("RGB", (w, h))
    bd = ImageDraw.Draw(band)
    for i in range(w):
        bd.line([(i, 0), (i, h)], fill=spectrum(i / max(1, w - 1)))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(
        [(0, h * .22), (w, 0), (w * .97, h), (w * .03, h * .78)], fill=255)
    canvas.paste(band, (x0, y0), mask)


def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)

    # soft colour glows
    glow = Image.new("RGB", (W, H), INK)
    gd = ImageDraw.Draw(glow)
    for cx, cy, r, col in [(260, 250, 360, (15, 155, 164)), (640, 180, 330, (242, 106, 60)),
                           (980, 300, 360, (253, 209, 10))]:
        for k in range(r, 0, -6):
            a = (1 - k / r) ** 2 * 0.13
            c = tuple(int(INK[i] + (col[i] - INK[i]) * a) for i in range(3))
            gd.ellipse([cx - k, cy - k, cx + k, cy + k], fill=c)
    im = glow.filter(ImageFilter.GaussianBlur(60))
    d = ImageDraw.Draw(im)

    # frame rails, like the deck
    for i in range(W):
        d.line([(i, 0), (i, 10)], fill=spectrum(i / (W - 1)))
        d.line([(i, H - 10), (i, H)], fill=spectrum(i / (W - 1)))

    f_small = poppins(20)
    tracked(d, (90, 118), "PONTIAC, MICHIGAN  ·  MEMORIAL DAY WEEKEND 2028", f_small, (170, 182, 184), 4)

    f_big = oswald(150)
    gradient_text(im, (84, 160), "AMERICA'S", f_big, tracking=2)
    f_mid = oswald(56, 600)
    gradient_text(im, (90, 350), "SPRING CANVAS FESTIVAL", f_mid, tracking=9)

    ribbon(im, (90, 448, 700, 470))

    f_body = poppins(24)
    d.text((90, 500), "Food, art, music and a conflict resolution campaign.", font=f_body, fill=(220, 230, 231))

    im.save(os.path.join(IMG, "og.png"), optimize=True)
    print("og.png", os.path.getsize(os.path.join(IMG, "og.png")) // 1024, "KB")


def touch_icon():
    S = 180
    im = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(im)
    f = oswald(118)
    gradient_text(im, (45, 8), "A", f)
    ribbon(im, (26, 132, 154, 148))
    im.save(os.path.join(IMG, "apple-touch-icon.png"), optimize=True)
    print("apple-touch-icon.png ok")


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="s" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#0F9BA4"/><stop offset=".4" stop-color="#F26A3C"/>
<stop offset=".78" stop-color="#B2CE3B"/><stop offset="1" stop-color="#FDD10A"/>
</linearGradient></defs>
<rect width="64" height="64" rx="12" fill="#070C0D"/>
<path d="M18 46 L28 14 H36 L46 46 H39 L37 39 H27 L25 46 Z M29 33 H35 L32 23 Z" fill="url(#s)"/>
<path d="M10 52 L54 49 L52.5 55 L11.5 56 Z" fill="url(#s)"/>
</svg>
"""


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    og()
    touch_icon()
    open(os.path.join(IMG, "favicon.svg"), "w").write(FAVICON)
    print("favicon.svg ok")

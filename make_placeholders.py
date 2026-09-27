#!/usr/bin/env python3
"""Regenerates assets/img placeholders.

No text inside the SVG: background-size:cover scales the artboard, so any
type baked in here balloons on narrow screens. Pattern only.
"""
import os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "img")

SPECS = [
    ("hero-crowd",    "#0F9BA4", "#07383C", 0),
    ("hero-food",     "#F26A3C", "#521E0E", 1),
    ("hero-art",      "#B2CE3B", "#3A480C", 2),
    ("hero-rps",      "#FDD10A", "#544402", 3),
    ("eateries",      "#F26A3C", "#55200E", 1),
    ("exhibits",      "#B2CE3B", "#3A480C", 2),
    ("entertainment", "#0F9BA4", "#07383C", 0),
    ("tournament",    "#FDD10A", "#544402", 3),
    ("attractions",   "#F59C22", "#573306", 1),
    ("mission",       "#2FA79C", "#0C3835", 0),
    ("kids",          "#B2CE3B", "#36430B", 2),
    ("fireworks",     "#F26A3C", "#3F1509", 3),
    ("sponsors",      "#0F9BA4", "#062F33", 0),
    ("banquet",       "#F59C22", "#4A2D06", 1),
]


def art(v):
    if v == 0:
        rings = "".join(f'<circle cx="300" cy="640" r="{r}"/>' for r in range(120, 900, 70))
        return f'<g fill="none" stroke="rgba(255,255,255,.07)" stroke-width="2">{rings}</g>'
    if v == 1:
        bands = "".join(
            f'<rect x="{-400 + i * 150}" y="-200" width="70" height="1200" '
            f'fill="rgba(255,255,255,.05)" transform="rotate(22 600 375)"/>' for i in range(14))
        return f"<g>{bands}</g>"
    if v == 2:
        random.seed(7)
        sq = "".join(
            f'<rect x="{random.randint(0, 1150)}" y="{random.randint(0, 700)}" '
            f'width="{random.choice([18, 26, 40])}" height="{random.choice([18, 26, 40])}" '
            f'fill="rgba(255,255,255,.055)"/>' for _ in range(46))
        return f"<g>{sq}</g>"
    rays = "".join(f'<line x1="600" y1="820" x2="{-200 + i * 110}" y2="-120"/>' for i in range(16))
    return f'<g stroke="rgba(255,255,255,.06)" stroke-width="3">{rays}</g>'


TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 750" width="1200" height="750" preserveAspectRatio="xMidYMid slice" role="presentation">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="{c1}" stop-opacity="0.34"/>
<stop offset="100%" stop-color="{c2}" stop-opacity="0.92"/>
</linearGradient>
<radialGradient id="v" cx="50%" cy="50%" r="72%">
<stop offset="55%" stop-color="#000" stop-opacity="0"/>
<stop offset="100%" stop-color="#000" stop-opacity="0.45"/>
</radialGradient>
</defs>
<rect width="1200" height="750" fill="#08100F"/>
<rect width="1200" height="750" fill="url(#g)"/>
{art}
<rect width="1200" height="750" fill="url(#v)"/>
</svg>
"""

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, c1, c2, v in SPECS:
        open(os.path.join(OUT, name + ".svg"), "w").write(TPL.format(c1=c1, c2=c2, art=art(v)))
    print("wrote", len(SPECS), "placeholders")

# NOTE: assets/img/hero-pontiac.svg (first homepage slide) is hand-authored,
# not generated here — it's the one intentionally vivid placeholder.

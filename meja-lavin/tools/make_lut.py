#!/usr/bin/env python3
"""Teal-Amber LUT: pulls the saturated cyan backdrop toward a deeper, quieter teal
and gives warm cover tones a touch more richness. Every change is weighted by the
pixel's own saturation, so greys, whites, skin and dark coats pass through smoothly
(no keyed edges). Writes grading/teal-amber.cube (33^3)."""
import colorsys, math, os
N = 33
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "grading", "teal-amber.cube")

def bump(h, c, w):  # smooth raised-cosine weight around hue c (degrees), half-width w
    d = abs(((h - c + 180) % 360) - 180)
    return 0.5 * (1 + math.cos(math.pi * d / w)) if d < w else 0.0

def ss(x, a, b):
    t = min(1, max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

lines = [f'TITLE "teal-amber"', f"LUT_3D_SIZE {N}", "DOMAIN_MIN 0 0 0", "DOMAIN_MAX 1 1 1"]
for bi in range(N):
    for gi in range(N):
        for ri in range(N):
            r, g, b = ri / (N - 1), gi / (N - 1), bi / (N - 1)
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hd = h * 360
            ws = ss(s, 0.12, 0.55) * ss(v, 0.08, 0.35)          # only clearly coloured, not-dark pixels
            cy = bump(hd, 195, 40) * ws                          # cyan / sky-blue backdrop
            am = bump(hd, 32, 28) * ws                           # amber / orange covers
            s2 = s * (1 - 0.40 * cy) * (1 + 0.08 * am)
            v2 = v * (1 - 0.16 * cy) * (1 + 0.02 * am)
            h2 = (hd - 7 * cy) / 360 % 1.0
            r2, g2, b2 = colorsys.hsv_to_rgb(h2, min(1, s2), min(1, v2))
            lines.append(f"{r2:.6f} {g2:.6f} {b2:.6f}")
open(out, "w").write("\n".join(lines) + "\n")
print("wrote", os.path.relpath(out))

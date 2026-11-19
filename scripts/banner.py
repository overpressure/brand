#!/usr/bin/env python3
# SPDX-License-Identifier: Unlicense
"""Draw the r/overpressure banner (1920 x 384) as SVG: a gauge face whose needle stands in the red zone.

    python scripts/banner.py && python scripts/render.py reddit/banner.png

The gauge's hub sits below the banner, right of its centre, so that the needle and the red zone show in every
crop Reddit makes (the whole banner, a thin desktop strip, a phone's centre); the left stays calm for the
community's icon and name.
"""

import math
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "reddit" / "banner.svg"

W, H = 1920, 384
CX, CY = 1240, 590  # the gauge's hub, below the banner
R_TICKS = 500
RED_FROM, RED_TO = 24, 50  # degrees from straight up, clockwise
NEEDLE = 38


def point(r: float, deg: float) -> tuple[float, float]:
    """Return the point @p r from the hub, @p deg clockwise from straight up."""
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def arc(r: float, a0: float, a1: float) -> str:
    """Return an SVG path along the circle of @p r from @p a0 to @p a1 degrees."""
    x0, y0 = point(r, a0)
    x1, y1 = point(r, a1)
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}"


parts = []
# Ticks: minor every 2 degrees, major every 10; the red zone's in orange.
for deg in range(-76, 77, 2):
    major = deg % 10 == 0
    length = 30 if major else 14
    red = RED_FROM <= deg <= RED_TO
    x0, y0 = point(R_TICKS, deg)
    x1, y1 = point(R_TICKS - length, deg)
    colour = "#ff7849" if red else "#ffffff"
    opacity = (0.9 if major else 0.6) if red else (0.22 if major else 0.10)
    width = 4 if major else 2.5
    parts.append(
        f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{colour}" '
        f'stroke-opacity="{opacity}" stroke-width="{width}" stroke-linecap="round"/>'
    )
ticks = "\n    ".join(parts)

# The needle: a long taper from the hub, through the red zone; its tip a little short of the ticks.
tip = point(R_TICKS - 40, NEEDLE)
a = math.radians(NEEDLE)
nx, ny = math.cos(a), math.sin(a)  # perpendicular to the needle
base_half = 15
b1 = (CX + nx * base_half, CY + ny * base_half)
b2 = (CX - nx * base_half, CY - ny * base_half)
needle = f"M{b1[0]:.1f} {b1[1]:.1f} L{tip[0]:.1f} {tip[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f} Z"

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>r/overpressure banner</title>
  <defs>
    <radialGradient id="glow-blue" cx="0.16" cy="0.5" r="0.62" gradientTransform="matrix(1 0 0 2.5 0 -0.75)">
      <stop offset="0" stop-color="#1b2f63"/><stop offset="0.55" stop-color="#14234a" stop-opacity="0.45"/>
      <stop offset="1" stop-color="#14234a" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-red" cx="{point(R_TICKS, NEEDLE)[0] / W:.3f}" cy="{point(R_TICKS, NEEDLE)[1] / H:.3f}"
                    r="0.12" gradientTransform="matrix(1 0 0 5 0 {-4 * point(R_TICKS, NEEDLE)[1] / H:.3f})">
      <stop offset="0" stop-color="#ff7849" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#ff7849" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="face" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.035"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="needle" gradientUnits="userSpaceOnUse" x1="{CX}" y1="{CY}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.55"/><stop offset="1" stop-color="#ffffff"/>
    </linearGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="12" cy="12" r="1.2" fill="#ffffff" fill-opacity="0.045"/>
    </pattern>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0d0e11"/><stop offset="0.12" stop-color="#0d0e11" stop-opacity="0"/>
      <stop offset="0.88" stop-color="#0d0e11" stop-opacity="0"/>
      <stop offset="1" stop-color="#0d0e11" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="#0d0e11"/>
  <rect width="{W}" height="{H}" fill="url(#glow-blue)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect width="{W}" height="{H}" fill="url(#glow-red)"/>
  <!-- The gauge's face: a faint disc and two rims -->
  <circle cx="{CX}" cy="{CY}" r="{R_TICKS + 40}" fill="url(#face)"/>
  <circle cx="{CX}" cy="{CY}" r="{R_TICKS + 40}" fill="none" stroke="#2a66ec" stroke-opacity="0.35" stroke-width="3"/>
  <circle cx="{CX}" cy="{CY}" r="{R_TICKS + 52}" fill="none" stroke="#2a66ec" stroke-opacity="0.12" stroke-width="10"/>
  <circle cx="{CX}" cy="{CY}" r="{R_TICKS - 120}" fill="none" stroke="#ffffff" stroke-opacity="0.05" stroke-width="2"/>
  <!-- The red zone, as on the logo's lenses -->
  <path d="{arc(R_TICKS + 14, RED_FROM, RED_TO)}" fill="none" stroke="#ff7849" stroke-width="22" stroke-linecap="round"
        stroke-opacity="0.55" filter="url(#soft)"/>
  <path d="{arc(R_TICKS + 14, RED_FROM, RED_TO)}" fill="none" stroke="#ff7849" stroke-width="12"
        stroke-linecap="round"/>
  <g>
    {ticks}
  </g>
  <!-- The needle, in the red -->
  <path d="{needle}" fill="#ffffff" fill-opacity="0.35" filter="url(#soft)"/>
  <path d="{needle}" fill="url(#needle)"/>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
</svg>
"""
out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
with out.open("w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(f"written {out}")

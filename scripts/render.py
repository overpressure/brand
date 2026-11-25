#!/usr/bin/env python3
# SPDX-License-Identifier: Unlicense
"""Render every PNG from its drawing, or check that every rendering is there at its size.

    python scripts/render.py --check      every rendering there, a PNG at its size (CI runs this)
    python scripts/render.py [PATH...]    render them (or the named ones) again through headless Chromium

A browser renders the drawings as browsers show them (gradients, round caps, filters), at the exact pixel
size each use takes; the window's Windows icon is assembled from its PNG renderings. The social cards have
no drawing of their own yet: --check only checks their size.
"""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
#: The installer's window takes the small drawing up to this size (pixels), the full one above.
SMALL_UP_TO = 48


@dataclass(frozen=True)
class Rendering:
    """One PNG (relative to the repository), the drawing it comes from, and its size in pixels."""

    png: str
    svg: str | None
    width: int
    height: int


def _window() -> list[Rendering]:
    # The installer's window (overpressure/window/logo.py): the small drawing up to 48 px, the full one above.
    found = [
        Rendering(
            f"window/app-{s}.png", "logo/overpressure-small.svg" if s <= SMALL_UP_TO else "logo/overpressure.svg", s, s
        )
        for s in (16, 20, 24, 32, 40, 48, 64, 80, 96, 112, 128, 144, 160, 192, 256)
    ]
    found += [
        Rendering(f"window/app-light-{s}.png", "logo/overpressure-light.svg", s, s)
        for s in (64, 80, 96, 112, 128, 144, 160, 192)
    ]
    found += [
        Rendering(f"window/mark-{h}.png", "logo/overpressure-mark.svg", 2 * h, h)
        for h in (24, 30, 36, 42, 48, 54, 60, 72)
    ]
    return found


RENDERINGS = [
    Rendering("github/avatar.png", "logo/overpressure.svg", 512, 512),
    *(
        Rendering(f"github/social/{name}.png", None, 1280, 640)
        for name in ("overpressure", "overpressure-light", "phoenix", "packages", "linux", "builder")
    ),
    *(
        Rendering(f"matrix/{name}.png", f"matrix/{name}.svg", 512, 512)
        for name in ("space", "general", "announcements", "help", "phoenix", "hollywood", "dev", "offtopic")
    ),
    Rendering("reddit/icon.png", "logo/overpressure.svg", 256, 256),
    Rendering("reddit/banner.png", "reddit/banner.svg", 1920, 384),
    *_window(),
]
#: Windows' icon: these sizes of the window's app icon in one file.
ICO = "window/overpressure.ico"
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 256)


def png_size(path: Path) -> tuple[int, int]:
    """Return the width and height of the PNG at @p path; ValueError for anything else."""
    head = path.read_bytes()[:24]
    if not head.startswith(PNG_SIGNATURE) or head[12:16] != b"IHDR":
        msg = f"{path} is not a PNG"
        raise ValueError(msg)
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def ico_sizes(path: Path) -> list[int]:
    """Return the sizes in the ICO file at @p path (256 is stored as 0)."""
    data = path.read_bytes()
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    if reserved != 0 or kind != 1:
        msg = f"{path} is not an icon"
        raise ValueError(msg)
    return [data[6 + 16 * i] or 256 for i in range(count)]


def check() -> list[str]:
    """Return what is missing or at the wrong size."""
    problems = []
    for r in RENDERINGS:
        if r.svg and not (ROOT / r.svg).is_file():
            problems.append(f"{r.png}: its drawing {r.svg} is missing")
        try:
            size = png_size(ROOT / r.png)
        except (OSError, ValueError) as exc:
            problems.append(f"{r.png}: {exc}")
            continue
        if size != (r.width, r.height):
            problems.append(f"{r.png}: {size[0]} x {size[1]}, not {r.width} x {r.height}")
    try:
        if sorted(ico_sizes(ROOT / ICO)) != sorted(ICO_SIZES):
            problems.append(f"{ICO}: sizes {ico_sizes(ROOT / ICO)}, not {list(ICO_SIZES)}")
    except (OSError, ValueError) as exc:
        problems.append(f"{ICO}: {exc}")
    return problems


def browser() -> str:
    """Return a Chromium to render with: CHROME, else one on PATH or in its usual place."""
    named = os.environ.get("CHROME")
    if named:
        return named
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    for path in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ):
        if Path(path).is_file():
            return path
    msg = "no Chromium found: set CHROME to one"
    raise FileNotFoundError(msg)


def render(r: Rendering, chrome: str) -> None:
    """Render @p r's drawing to its PNG at its size, on a transparent background."""
    if r.svg is None:
        msg = f"{r.png} has no drawing to render from"
        raise ValueError(msg)
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(
            "<!doctype html><html><head><style>html,body{margin:0;background:transparent}img{display:block}"
            f'</style></head><body><img src="{(ROOT / r.svg).as_uri()}" width="{r.width}" height="{r.height}">'
            "</body></html>",
            encoding="utf-8",
        )
        out = Path(tmp) / "out.png"
        subprocess.run(  # a browser the owner has, fixed arguments
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--default-background-color=00000000",
                f"--window-size={r.width},{r.height}",
                f"--screenshot={out}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        if png_size(out) != (r.width, r.height):
            msg = f"{r.png}: the browser rendered {png_size(out)}"
            raise ValueError(msg)
        shutil.copyfile(out, ROOT / r.png)
    print(f"rendered {r.png} ({r.width} x {r.height})")


def write_ico() -> None:
    """Assemble the Windows icon from the app icon's PNG renderings (an ICO holds PNGs as they are)."""
    images = [(size, (ROOT / f"window/app-{size}.png").read_bytes()) for size in ICO_SIZES]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, data = b"", b""
    for size, png in images:
        side = 0 if size >= 256 else size  # noqa: PLR2004  # the format stores 256 as 0
        entries += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(png), offset + len(data))
        data += png
    (ROOT / ICO).write_bytes(header + entries + data)
    print(f"assembled {ICO} ({', '.join(map(str, ICO_SIZES))})")


def main(argv: list[str]) -> int:
    """Check, or render the named renderings (all by default)."""
    if argv[:1] == ["--check"]:
        problems = check()
        for line in problems:
            print(line, file=sys.stderr)
        print(f"{len(RENDERINGS) + 1} renderings checked, {len(problems)} problem(s)")
        return 1 if problems else 0
    wanted = {Path(a).as_posix() for a in argv}
    chrome = browser()
    for r in RENDERINGS:
        if r.svg and (not wanted or r.png in wanted):
            render(r, chrome)
    if not wanted or ICO in wanted or any(w.startswith("window/app-") for w in wanted):
        write_ico()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

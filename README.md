<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logo/overpressure.svg">
    <img src="logo/overpressure-light.svg" width="128" height="128" alt="The overpressure logo: a headset whose two lenses are pressure gauges reading in the red">
  </picture>
</p>

# overpressure brand

**TL;DR.** Every drawing and rendering of [overpressure](https://github.com/overpressure/overpressure): the
logo's drawings in [logo/](logo/README.md), and what each place gets, in a folder per place (GitHub, Matrix,
Reddit, the installer's window). The drawings are the source; every PNG is rendered from them
(`python scripts/render.py`). The artwork is under [CC BY-SA 4.0](LICENSE), the scripts under the
[Unlicense](scripts/LICENSE); the name and the logo stand for the project ([TRADEMARK.md](TRADEMARK.md)).

## Where each file goes

| Folder | What | Where it is used |
| --- | --- | --- |
| [logo/](logo/README.md) | The drawings: the app icon on a dark and a light tile, its small version, the mark without the tile, one colour | Everything else here; the READMEs of overpressure's repositories |
| [github/](github/) | `avatar.png` (512 × 512); `social/` with each repository's social preview (1280 × 640) | The organization's avatar and each repository's *Social preview*, uploaded in their settings |
| [matrix/](matrix/) | The space's and each room's icons (`.svg`, 512 × 512 `.png`) | The Matrix space `#overpressure:matrix.org` and its rooms, each room's settings |
| [reddit/](reddit/) | `icon.png` (256 × 256), `banner.svg` and `banner.png` (1920 × 384) | r/overpressure's *Community appearance* |
| [window/](window/) | The app icon (16 to 256 px, light from 64), the mark by height (24 to 72 px), `overpressure.ico` | The installer's window; overpressure/overpressure carries a copy in `overpressure/window/icons/` |
| [mockups/](mockups/) | [mockups.html](mockups/mockups.html) (the logo in use, light and dark), previews of the Matrix icons and the Reddit banner's crops | Looking at the artwork in place before uploading it |

The headset's boot screen draws the mark from the same geometry in its own code
([pico4-splash.c](https://github.com/overpressure/phoenix/blob/main/src/splash/pico4-splash.c)).

## Colours

| | |
| --- | --- |
| Visor | `#5a92ff` → `#2a66ec` → `#1a43b8` |
| Lenses | `#0b0d12` |
| Red zone | `#ff7849` |
| Needle and hub | `#ffffff` |
| Dark tile | `#2b2e35` → `#0f1013` |
| Light tile | `#ffffff` → `#eef0f3` |
| Dark backgrounds (social card, banner) | `#0d0e11` with a `#14234a` glow |

## Rendering

```sh
python scripts/render.py               # every PNG again from its drawing, and window/overpressure.ico
python scripts/render.py reddit/banner.png
python scripts/render.py --check       # every rendering there, at its size (CI runs it)
python scripts/banner.py               # the Reddit banner's drawing, from its parameters
```

A Chromium renders the drawings as browsers show them, at each file's exact size, on a transparent background
(`CHROME` names one if it isn't found). After a drawing changes, render its PNGs again rather than editing
them, and upload what changed where the table says. The social cards have no drawing of their own yet.

## Changes

By pull request, like every repository of the organization
([GOVERNANCE.md](https://github.com/overpressure/.github/blob/main/GOVERNANCE.md)). A change to the logo itself
is discussed in an issue first.

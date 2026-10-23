# Troubleshooting

## Setup

**`No Chromium found` or a Playwright launch error.**
Run `~/.cache/logo-doctor/venv/bin/python -m playwright install chromium`. On a fresh Linux machine Chromium may also
need system libraries: `sudo ~/.cache/logo-doctor/venv/bin/python -m playwright install-deps chromium`. If the
download is blocked, install Google Chrome or Chromium from your package manager; the tool falls back to it.

**`python3 -m venv` fails on Debian or Ubuntu.** Install the venv module: `sudo apt install python3-venv`.

**Windows.** Use WSL, or create a virtual environment, `pip install -r requirements.txt`, then
`python -m playwright install chromium`.

## Reading the results

**Many findings on a hand-drawn or traced logo.** Such marks are not built from exact circles and a grid, so the
tool finds many small differences. Read them as a pattern ("the curves are freehand", "the mark has no grid") and
decide whether the style should be constructed at all.

**A tapering stroke is reported as uneven.** The tool cannot know the taper is intended. If it is, ignore the point.

**No grid found, but the mark was built on one.** Pass `--grid` with the module (and `--grid-origin` if the grid does
not start at the file's origin). Grids in other units, or rotated grids, are not detected.

**Positions are off the grid by the same amount everywhere.** The grid origin differs; pass `--grid-origin`.

**The angle check flags deliberate angles.** Use `--snap 30` or `--snap 15` for marks built on those systems, or
`--snap 0` to turn the check off.

**Colours look slightly different from the official values.** For an SVG, colours come from the file. For a raster
they are sampled and can be a few steps off; pass `--colours` with the official values.

**Measurements on a PNG differ by a fraction from the SVG.** Rasters are less exact. Use the SVG whenever there is
one; for a raster-only logo, the logo-repolish skill can rebuild a precise vector first.

## Errors

**`... already has files. Choose a new folder, or pass --force`.** Reviews never overwrite earlier ones. Use a new
folder.

**`No logo found in the file`.** The image is empty or the background is not plain. Crop the logo onto a plain
background, or use a version with transparency.

**`the SVG has neither a viewBox nor a width and height`.** Add a `viewBox` to the root `<svg>` element.

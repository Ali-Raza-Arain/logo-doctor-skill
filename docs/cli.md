# Command line reference

All tools run with the Python from the setup (`~/.cache/logo-doctor/venv/bin/python`), or any Python with
`requirements.txt` installed and Chromium for Playwright.

## review.py

```
python skills/logo-doctor/scripts/review.py LOGO --out FOLDER [options]
```

`LOGO` is an SVG (measured in its own units, most precise) or a PNG, JPG or WebP (measured in source pixels).

| Option | Default | Meaning |
|---|---|---|
| `--out FOLDER` | required | new or empty folder for the results |
| `--name NAME` | file name | name used in the report title and brief |
| `--snap DEG` | 45 | angle system: edges are compared with multiples of this angle; 0 turns the check off |
| `--grid UNITS` | detected | the construction grid module, if known |
| `--grid-origin X,Y` | 0,0 | origin of the grid given with `--grid` |
| `--bg "NAME=#hex"` | none | extra background for the colour checks; repeat for several |
| `--colours "#hex,#hex"` | from the file | official logo colours, if the file's colours are not final |
| `--baseline FILE` | none | `findings.json` of an earlier review; the scorecard gains a Before column |
| `--force` | off | write into a folder that already has files |

### Output

| File | Content |
|---|---|
| `report.md` | scorecard, fix first (grouped, in order), consider, and every measurement with its image |
| `fix-brief.md` | instructions for an agent editing the SVG, and a brief for a designer |
| `findings.json` | statuses, summaries, fixes and key numbers, for `--baseline` |
| `01-grid.png` | grid lines, key positions on and off the grid, near misses |
| `02-strokes.png` | circles inside every stroke, coloured by deviation from its weight |
| `03-gaps.png` | circles in every gap between facing edges, coloured against the usual gap |
| `04-circles.png` | every arc as its full circle with its centre; rings labelled |
| `05-angles.png` | straight edges on and off the angle system |
| `06-symmetry.png` | where the mark differs from its best mirror or rotation |
| `07-balance.png` | centre of the ink, centre of the box, ink per quarter |
| `08-sizes.png` | 16 to 128 px on white and near-black, blur test, silhouette |
| `09-colour-backgrounds.png` | the logo on six backgrounds (and yours) with contrast, plus suggested versions |
| `10-colour-vision.png` | protanopia, deuteranopia, tritanopia and greyscale |

Statuses: **Fix** (an objective fault), **Check** (a judgment to make), **Pass**, **Info**.

### Examples

```bash
# a first review
python review.py brand/logo.svg --out review-1 --name "<Brand>" --bg "navy=#0e1f38"

# after fixing a copy, compare with the first review
python review.py brand/logo-v2.svg --out review-2 --name "<Brand>" --baseline review-1/findings.json

# a mark built on 30 degree angles and a known 12-unit grid
python review.py mark.svg --out review --snap 30 --grid 12
```

## examples/make_demo.py

```
python examples/make_demo.py FOLDER [--colour #1d5e74]
```

Writes `demo-draft.svg` (six known faults) and `demo-fixed.svg`.

## tests/smoke_test.py

```
python tests/smoke_test.py [--keep FOLDER]
```

Builds the demo marks, reviews them as SVG and PNG, and checks that the draft's faults are found and the fixed mark
passes.

## tools/make_readme_images.py

Rebuilds `examples/` (demo marks and both sample reviews) and the images in `docs/images`.

## tools/package_skill.py

Checks the skill's name and description and writes `dist/logo-doctor.zip` and `dist/logo-doctor.skill`.

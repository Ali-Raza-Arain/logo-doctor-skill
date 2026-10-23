---
name: logo-doctor
description: Review a logo the way a senior identity designer does, with measurements, and give prioritised feedback on how to fix it. Measures the construction grid, stroke weights (circles fitted in every stroke), gaps, rings, arcs and shared centres, angles, alignment, symmetry, balance, small sizes, and colour on light, mid and dark backgrounds, for colour-blind viewers and in greyscale, with annotated images and a before and after scorecard. Also holds the rules for designing a mark, fixing methods, colour selection with dark and light versions, and prompts and briefs for an agent, a designer or an image tool. Use it whenever the user asks to check, audit, critique, rate, improve or fix a logo, icon or brand mark, asks if a logo follows design rules or looks professional, which colours or backgrounds suit it, how it works on dark and light backgrounds, or wants rules or a prompt for making a logo, even if they only ask "is my logo good".
license: MIT, see LICENSE.txt. Bundled font under the SIL Open Font License, see assets/fonts/OFL.txt.
metadata:
  author: Ali Raza
  version: 1.0.0
  source: https://github.com/ali-raza-arain/logo-doctor-skill
---

# Logo doctor

Examine a logo like a senior identity designer: measure what can be measured, judge what needs judgment, and
give the owner feedback they can act on, in order of importance, with the evidence.

The tool finds construction faults with precision, but it does not know intent. A tapering stroke, a deliberate
offset or an optical correction will be flagged. Your job is to verify every flag against the images and the
references, keep what is a real fault, explain what is a choice, and add what no measurement can see: concept,
fit, distinctiveness and feeling.

## Ground rules

1. **Local only.** Never upload the logo, or anything made from it, to a website, image generator, design tool,
   cloud storage, artifact, gist or paste service. Everything here runs on this machine. If something seems to
   need an online service, stop and ask.
2. **Never change the logo on your own.** Do not recolour, redraw or "improve" the owner's file. Report, suggest
   and show options; edit only after the owner agrees, and then only a copy.
3. **Never overwrite.** Write reviews into new folders (the script refuses non-empty ones unless `--force`).
4. **Be honest.** Say what the measurements found and how sure they are. Separate faults from taste. Never claim
   that a logo is original or legally safe; that needs a trademark search by a professional.
5. **Look before you speak.** Open every image the review writes (with the file-reading tool) before you describe
   it. Do not report a finding you have not seen in the images.

## Setup (once per machine)

```bash
bash <skill>/scripts/setup_env.sh
PY=~/.cache/logo-doctor/venv/bin/python
```

`<skill>` is this skill's folder. Rendering uses a headless Chromium, so SVGs are measured exactly as browsers
draw them.

## Workflow

### 1. Gather

Find out, from the user or their files, before you run anything:
- **The best file.** SVG measures to a fraction of a unit; a raster is less exact. If only a PNG or JPG exists,
  say so, and if the logo-repolish skill is installed, offer to rebuild a vector first.
- **The official colours** (hex codes), if the file's colours are not final.
- **Where the logo lives:** website, app icon, social avatars, print, signage, merchandise. This decides which
  sizes and backgrounds matter.
- **The backgrounds it must sit on**, especially the brand's own dark and light colours.
- **The brief:** what the business does and who it is for, so you can judge fit.

If the user just wants a quick check, run the review and ask these questions alongside the results.

### 2. Measure

```bash
$PY <skill>/scripts/review.py logo.svg --out review-1 --name "Brand" [--bg "navy=#0e1f38"] [--colours "#hex,#hex"]
```

Options: `--snap 30` (or 15, or 0) when the design uses another angle system; `--grid 20` when the module is known;
`--bg` for each brand background; `--baseline old/findings.json` to compare with an earlier review.

It writes `report.md` (scorecard, fix first, consider, details), `fix-brief.md`, `findings.json` and ten images:
grid, strokes, gaps, circles, angles, symmetry, balance, sizes, colour on backgrounds, colour vision.

### 3. Verify every flag

Open `report.md` and every image. For each item, decide: real fault, intended choice, or measurement artefact.
`references/measurements.md` explains how each check works and its known false positives. Typical judgments:
- A stroke that varies in width may be designed contrast (calligraphic or typographic marks), not an error.
- Two weights 3 to 10% apart in a geometric mark are almost always an error; in a hand-drawn mark, often texture.
- Positions off a grid matter in a constructed mark; a freehand mark may have no grid at all.
- Round parts reaching a little past flat edges may be optical overshoot, which is correct.

Drop what you dismiss, and say briefly why, so the owner learns the reasoning.

### 4. Review what measurements cannot see

Work through `references/principles.md`: the brief and fit, the five qualities (simple, memorable, timeless,
versatile, appropriate) with their tests, space and figure-ground, optical corrections, type in the logo, the
logo system, originality and legal risk. Use `08-sizes.png` (blur, silhouette, small sizes) for the quick visual
tests. `references/construction.md` holds the construction rules a senior designer applies.

### 5. Plan colour

Read `09-colour-backgrounds.png` and `10-colour-vision.png` with `references/colour.md`. Say where the colour
works, where it fails, and what to use there: a lighter or darker version with the same hue (the review proposes
one), or the one-colour white or black version. Proposals need the owner's approval.

### 6. Write the feedback

Follow `references/feedback.md`: a short verdict, what is strong, what to fix first (with the image and the
numbers), what to consider, the colour plan, the small-size plan, and next steps. Plain words, the user's language,
no jargon without a short explanation. Point to the image for each finding.

### 7. Fix, only when asked

Offer to fix the confirmed faults. Methods for each kind of fault are in `references/fixing.md`; for a constructed
mark, rebuilding it from exact geometry is usually cleaner than nudging points. Work on a copy, then run the review
again with `--baseline` and show the before and after scorecard. If logo-repolish is installed, use it to export
the kit from the fixed master.

### 8. Hand off, when someone else will fix it

`fix-brief.md` is written for both an agent and a designer. Edit it with your verified judgment before handing it
over: remove dismissed items, add the fit and concept points. More prompt templates, including briefs for a new
mark and for image tools, are in `references/prompts.md`.

## Designing a new mark

When the user wants a logo made rather than reviewed, follow the process in `references/principles.md`
(section Process): brief, research, concepts as sketches in words or simple shapes, construction on a grid, then
refinement. Build marks as exact geometry (the demo generator in this skill's repository, `examples/make_demo.py`,
shows the approach), check every round with `review.py`, and present two or three directions with their reasoning.
Never present a mark as original or registrable without a trademark search.

## Files

```
scripts/review.py      runs everything; writes the report, the fix brief, findings.json and ten images
scripts/measure.py     geometry: strokes, gaps, outline, circles, angles, grid, alignment, symmetry, balance
scripts/colours.py     contrast, colour vision simulation, lightness variants, colour sheets
scripts/common.py      loading SVG and raster logos, rendering, colour maths, drawing
scripts/setup_env.sh   one-time environment setup
references/principles.md    what a senior designer checks, the process for new marks, legal basics
references/construction.md  grids, weights, gaps, curves, angles, terminals, optical corrections
references/colour.md        choosing colours, light and dark versions, print, colour vision
references/fixing.md        how to fix each kind of fault, and how to verify
references/prompts.md       prompts and briefs for agents, designers and image tools
references/feedback.md      how to write the review
references/measurements.md  how each check works, its thresholds and false positives
```

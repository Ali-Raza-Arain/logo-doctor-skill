# How the measurements work

What each check in `review.py` computes, its thresholds, and the cases where it flags something that is not a
fault. Read the matching section before you report a finding you are unsure about.

## Contents

1. [Loading and units](#1-loading-and-units)
2. [Stroke weights](#2-stroke-weights)
3. [Gaps](#3-gaps)
4. [Outline: lines, arcs, corners](#4-outline-lines-arcs-corners)
5. [Circles, rings and centres](#5-circles-rings-and-centres)
6. [Angles](#6-angles)
7. [Grid](#7-grid)
8. [Alignment](#8-alignment)
9. [Symmetry](#9-symmetry)
10. [Balance and complexity](#10-balance-and-complexity)
11. [Small sizes](#11-small-sizes)
12. [Colour](#12-colour)

## 1. Loading and units

An SVG is rendered by headless Chromium around its ink, so the larger side of the mark is about 2000 pixels, with
a margin. Results are converted back to the SVG's own units. A raster is enlarged (bicubic, up to 4x) to the same
working size and measured in source pixels; its edges are less exact, so tolerances are wider.

Colours come from the fills and strokes named in the SVG (or the official colours passed with `--colours`); each
pixel is assigned to the nearest one. Gradients are measured as their nearest flat colour.

Every edge is read at sub-pixel precision from the antialiased render (the level where coverage is one half).

## 2. Stroke weights

The centre line of every stroke is found by thinning the shape to a one-pixel skeleton. At each point the width is
the distance to the nearest edge plus the distance to the nearest edge on the other side, which stays exact even
when the skeleton pixel is not quite in the middle. Points near junctions and loose ends are left out, because
there the largest circle that fits is not the stroke width.

Each connected run of centre line is one part; its width is the median along it. Parts are grouped into weights:
values that run into each other within 4% are one weight. Adjacent weights less than 15% apart are reported as
"two weights where one is intended".

Horizontal and vertical parts of the main weight are compared for the optical note.

False positives:
- Strokes that taper on purpose (calligraphic marks, contrast in letterforms) are reported as varying.
- Very short parts between two junctions can be measured from too few points; check them in the image.
- Solid shapes (a filled square or disc) have no stroke weight; their "width" is their size.

## 3. Gaps

The same method on the empty space: the skeleton of the background, kept only where the space has the mark on both
sides (a step from the nearest edge through the point and on by a little more meets the mark again). This drops
the margin around the logo, wide open areas and the spurs a skeleton grows into corners. Spaces wider than three
stroke widths (or 8% of the size) are counters or open space, not gaps.

- Usual gap: the length-weighted median of all gaps.
- Uneven: a gap whose 5th to 95th percentile widths differ by more than 15% of its median, over a length of at
  least three times its width.
- Tight: a gap whose narrow end is under 70% of the usual gap, or under 60% of the main stroke weight.

False positives: a ring next to a straight edge makes a gap that is narrow at one point by nature; it is still a
tight spot if it is much narrower than the usual gap, but say so in plain words.

## 4. Outline: lines, arcs, corners

Each outline is resampled every pixel and split greedily into the longest straight run or circular arc that fits
within half a pixel (wider for rasters). Lines are refitted on their middle 70%, arcs on their middle 85%, so the
transitions do not tilt them. A short run that fits a circle much better than a line is treated as the start of a
curve, not as a line.

A corner is where two straight runs, each longer than 2% of the size, meet at 20 degrees or more within a short
distance; its position is the exact intersection of the two lines.

## 5. Circles, rings and centres

Arcs (span of at least 20 degrees and a minimum length) are grouped by centre: centres within about 0.15% of the
size are the same centre.

- Ring: a full circle on the inside (span 300 degrees or more) and an outer arc of larger radius around the same
  centre. Dot: a full outer circle with no hole. Round hole: a full inner circle alone.
- Rings that look alike (similar sizes) but differ by more than half a unit or 1% are reported to match.
- Near-miss centres: groups of substantial arcs (90 degrees or more in total) whose centres are within 1.5% of the
  size but not identical. These are almost always meant to be concentric.
- Close radii: radii of the same kind of edge, around different centres, that differ by 1 to 5%. Reported as a
  point to consider, because many marks use different radii on purpose.

False positives: a traced or hand-drawn curve is a chain of slightly different arcs, so it produces many close radii
and near-miss centres. In such a mark, report the pattern once ("the curves are not built from circles") rather
than each pair.

## 6. Angles

Straight edges longer than 3.5% of the size (5% for rasters) are measured. Each is compared with the nearest
multiple of `--snap` (45 degrees by default). An edge is on the system if it is within 0.15 degrees, or the
measuring precision for its length; it is reported if it is off by more than that but less than 6 degrees.
Angles are given with 0 as horizontal and 90 as vertical, counter-clockwise, y up.

False positives: a deliberately different angle within 6 degrees of the system (rare). Use `--snap 0` for marks
without an angle system, or `--snap 30` or `15` for marks built on those.

## 7. Grid

Key positions: long vertical and horizontal edges, centres of substantial arcs, and true corners. Candidate modules
are round numbers from the file's origin (1, 2, 2.5, 4, 5, 8, 10 and their powers of ten) and whole fractions of
the mark's height or width from its top left corner (which finds grids drawn around the mark, and grids in a
raster at any scale). Each candidate is scored by how many positions fall within tolerance of a grid line, beyond
what chance would give for that module size. The largest module scoring near the best wins; round numbers are
preferred when close. Fewer than eight positions are too few to infer a grid.

Off-grid edges are paired: two edges of one stroke off by opposite amounts mean the stroke has the wrong width; by
the same amount, the stroke sits in the wrong place.

False positives: a mark built on a grid with a different origin, or on a grid in another unit, may be reported off
by a constant; pass `--grid` and `--grid-origin` when known. Freehand marks have no grid by design.

## 8. Alignment

Vertical and horizontal edges and centres (corners are left out) that run into each other within 1.2% of the size
form a group; a group whose members spread by more than the tolerance is a near miss. When a grid was found, only
groups with an off-grid member are reported, and those already covered by a grid fix are not repeated.

## 9. Symmetry

The mark is compared with its left-right mirror image, its top-bottom mirror image and its rotation by 180 degrees.
The copy is first moved to the position where it overlaps best (coarse search, then fine), so a mark that is
symmetric except for one part still lines up, and only that part shows. Verdicts:
- symmetric: the largest difference is under 0.25% of the size (or 1.5 pixels);
- nearly: 97% of the ink is within 3% of the size of the copy, and the largest difference is under 6%;
- not symmetric otherwise (by design, for most marks).

The image paints ink only in the mark red and ink only in the copy blue.

## 10. Balance and complexity

Balance: the centre of the ink compared with the centre of the bounding box, as a share of the width and height,
and the share of ink in each quarter. Over 3% off centre is noted. Complexity: parts, enclosed counters, lines,
arcs, and an edge index (outline length over the square root of the ink area).

## 11. Small sizes

The mark is reduced to 16, 24, 32, 48, 64 and 128 pixels (high-quality Lanczos reduction) on white and near-black,
shown enlarged with visible pixels. The narrowest gap gives the height below which gaps fill in (the gap falls
under one pixel). Also: a blur test (Gaussian, 2.5% of the size) and a silhouette (all counters filled).

## 12. Colour

- Contrast: WCAG 2 contrast ratio of each logo colour on each background.
- Variants: in OKLCH, lightness moves away from the background in small steps, with hue and chroma kept (chroma
  is reduced only to stay inside sRGB), until the ratio reaches 4.5:1. One lighter version for dark backgrounds
  (luminance under 0.1) and one darker version for light backgrounds (luminance 0.4 and over). Mid tones get advice
  instead of a variant.
- Colour vision: the Machado, Oliveira and Fernandes (2009) matrices at full severity, in linear RGB; greyscale is
  relative luminance. Two logo colours closer than 0.06 in OKLab under a simulation, but at least 0.1 apart in normal
  vision, are reported as merging.

# Construction rules

How a constructed mark is built and what makes it look precise. Each section says what `review.py` measures for
it, so you can match a finding to its rule.

## Contents

1. [Grid](#1-grid)
2. [Stroke weights](#2-stroke-weights)
3. [Gaps and rhythm](#3-gaps-and-rhythm)
4. [Curves, circles and centres](#4-curves-circles-and-centres)
5. [Angles](#5-angles)
6. [Terminals, joins and corners](#6-terminals-joins-and-corners)
7. [Alignment](#7-alignment)
8. [Optical corrections](#8-optical-corrections)
9. [Geometry first, optics second](#9-geometry-first-optics-second)

## 1. Grid

A grid is a module (a unit of length) repeated in both directions. Key positions sit on it: straight edges,
centres of circles and arcs, and corners.

- **Choosing a module.** Use a value that divides the stroke weight and the gap, so both are whole numbers of
  modules. With stroke 40 and gap 40, a module of 20 or 40 works; most logos use a module between 1/20 and 1/60 of
  the mark's height.
- **Major lines.** Every fifth (or fourth) line drawn stronger helps reading proportions: a mark that is 36 by 42
  modules says more than 720 by 840 units.
- **Keylines.** Some systems add a circle and a square of the same visual size inside the grid to size round and
  square marks consistently (used for icon sets). Useful for app icons.
- **Ratios.** Proportions such as 1:2 or 2:3 between parts read as deliberate. The golden ratio is one option among
  many; claims that it makes a mark better are not supported by evidence, so use it only if it helps decisions.
- **When there is no grid.** A freehand or calligraphic mark may have none, and that can be right. A geometric
  mark without one usually shows it: slightly different widths and near misses everywhere.

*Measured:* `01-grid.png` shows the detected module and every key position, green on the grid and red off it
with the offset.

## 2. Stroke weights

- **One weight, or clearly different weights.** A geometric mark usually has one stroke weight, sometimes two. A
  difference under about 10% reads as a mistake; 20% or more reads as a decision.
- **Ring and dot thickness** count as strokes and should match the stroke weight or a clear tier.
- **Even along the stroke.** A constant-width stroke should not swell or pinch. If it varies, the variation should
  follow a rule (contrast in a letterform, a taper to a point).
- **Horizontal and vertical.** The eye sees a horizontal stroke as heavier than a vertical one of the same width.
  Type designers make horizontals thinner (often 5 to 10%). In a monoline geometric mark this is optional; at large
  sizes it can matter.

*Measured:* `02-strokes.png` places circles inside every stroke; each circle's diameter is the stroke's width at
that point. Colours show the deviation from the stroke's weight.

## 3. Gaps and rhythm

- **Parallel strokes stay parallel.** The gap between two strokes that run side by side must be constant along
  their whole length, including around bends.
- **A clear ratio.** The gap is equal to the stroke, or a simple ratio of it (1:2, 2:3). Gap equal to stroke gives
  an even, calm texture.
- **No tight spots.** Places where two shapes come much closer than the usual gap (a ring near a trace, a corner
  near a curve) close up first at small sizes and in print, and they create dark spots.
- **Counters** (enclosed spaces) should be large enough to stay open at the minimum size.

*Measured:* `03-gaps.png` places circles in every gap between facing edges and colours them against the usual gap.

## 4. Curves, circles and centres

- **Concentric bends.** When parallel strokes turn a corner together, their arcs must share one centre, with radii
  that differ by stroke plus gap. Arcs with the same radius but different centres, or a centre that is slightly
  off, make the gap pinch or widen in the bend. This is the most common fault in generated and traced artwork.
- **A small set of radii.** Corner radii and curve radii come from a short list, ideally related to the module.
  Radii that differ by a hair (1 to 5%) look like mistakes.
- **Matching circles.** Dots, rings and holes that look alike must be identical: the same hole radius and the same
  outer radius.
- **Smooth joins.** Where a curve meets a straight line, the line should be tangent to the curve; a kink where they
  meet is visible at large sizes.
- **True circles.** A circle in a logo should be a true circle, not a polygon or an ellipse that is almost round.

*Measured:* `04-circles.png` draws every arc as its full circle, with its centre. Arcs that share a centre share a
colour; a centre that misses its partners is red.

## 5. Angles

- **An angle system.** Constructed marks use a small set of angles, usually multiples of 45 degrees, sometimes 30
  or 15. Everything that looks like 45 degrees should be exactly 45.
- **Consistent cuts.** All terminal cuts (the ends of strokes cut at an angle) use the same angle.
- **Parallel means parallel.** Edges that look parallel must be exactly parallel.

*Measured:* `05-angles.png` measures each straight edge; red ones are a few degrees off the system.

## 6. Terminals, joins and corners

- **Terminals** (stroke ends) share one treatment: all square, all round, or all cut at the same angle.
- **Joins** where strokes meet get heavy: two overlapping strokes make a dark spot. Type designers thin the
  strokes slightly where they meet (ink traps in small text fonts) so the joint looks the same weight.
- **Corners** are either all sharp or all rounded with the same radius. Sharp corners at 45 degrees or less can
  look like spikes at large sizes; a tiny radius is sometimes added.
- **Where a stroke meets a ring,** a small fillet or a clean tangent join both work; mixing them does not.

## 7. Alignment

- Edges and centres either line up exactly or are clearly offset (by at least a module). A miss of a fraction of
  a module looks like an error.
- Check centres of circles against each other, ends of strokes against each other, and the mark against the name
  in a lockup (cap height, baseline, centre).

*Measured:* near misses are drawn as dashed amber lines in `01-grid.png`.

## 8. Optical corrections

Geometry that is exactly right can look wrong. These corrections are applied on purpose, after the geometry is
exact, and only where they help.

- **Overshoot.** Round and pointed shapes look smaller than flat ones of the same height. They are drawn slightly
  larger, reaching past the flat line by roughly 1 to 3% of the height, so they look equal. A circle next to a
  square of the same height looks smaller; enlarge it.
- **Horizontal thinning.** Horizontal strokes look heavier than vertical ones of the same width (section 2).
- **Optical centre.** An object centred in a frame looks low. Place it slightly above the geometric centre.
- **Upper parts smaller.** In stacked forms (S, B, 8, 3) the upper part is drawn slightly smaller or narrower so
  the form does not look top-heavy.
- **Irradiation.** Light shapes on a dark background look larger and bolder than dark shapes on light. For a
  reversed (light on dark) version used small, consider a slightly lighter weight.
- **Junction thinning.** Where strokes meet or cross, thin them a little so the joint does not look like a blob
  (section 6).

`review.py` flags some of these as points to consider; the rest need your eye on the full-size and small renders.

## 9. Geometry first, optics second

Make the geometry exact (grid, weights, gaps, centres, angles), check it with `review.py`, and only then apply
optical corrections by eye. Apply each correction deliberately and record it, so the next review can tell it
apart from an error. An exact mark with no corrections is often good enough for a geometric style; an inexact
mark with corrections is never good.

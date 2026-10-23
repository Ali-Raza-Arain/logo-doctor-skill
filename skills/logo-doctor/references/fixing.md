# Fixing what the review finds

Methods for each kind of finding, and how to confirm the fix. Work only on a copy of the owner's file, and only
for the items the owner agreed to.

## Contents

1. [The fix loop](#1-the-fix-loop)
2. [Three ways to edit](#2-three-ways-to-edit)
3. [By finding](#3-by-finding)
4. [Small sizes: the simplified mark](#4-small-sizes-the-simplified-mark)
5. [Colour variants](#5-colour-variants)
6. [After the fixes](#6-after-the-fixes)

## 1. The fix loop

1. Copy the file (`logo-v2.svg`); never edit the original.
2. Fix in the order of the report: geometry (centres, angles), then weights and gaps, then positions, then
   symmetry. Later items often disappear when earlier ones are fixed: a stroke that is too wide also puts both of
   its edges off the grid; a centre that is off also makes a gap uneven and breaks symmetry.
3. Run the review on the copy with the earlier findings as the baseline:
   `review.py logo-v2.svg --out review-2 --baseline review-1/findings.json`
4. Compare the scorecards and the images. Confirm every fixed item and check that nothing else changed (the
   `compare` step in the logo-repolish skill can overlay two versions if it is installed).
5. Repeat until the Fix list is empty, then do the optical pass by eye (`construction.md`, section 8).

## 2. Three ways to edit

- **Rebuild from geometry (best for constructed marks).** Describe the mark as numbers: grid, stroke weight, gap,
  centres, radii, angles. Generate the SVG from them in a short script. Every fix is then a change to one number,
  and the result is exact by construction. `examples/make_demo.py` in this skill's repository builds a circuit S
  this way, with exact concentric arcs and 45 degree cuts.
- **Edit the path data.** For small corrections in a clean SVG, change coordinates directly in the `d`
  attribute. Absolute commands (M, L, A, C in capitals) are easiest to edit; convert relative ones first if needed.
  Keep the path closed and the fill rule unchanged.
- **Design tool.** In Figma, Illustrator or Inkscape: set a grid with the module from the review, turn on snapping
  to grid and points, fix the shapes, outline strokes, and export SVG without transforms (flatten them). Check
  the export with the review; design tools sometimes round coordinates.

## 3. By finding

**Positions off the grid.** Move the edge, centre or corner to the grid line the report names. If both edges of a
stroke are off by opposite amounts, the stroke has the wrong width: fix the width instead (the report says so).
If both are off by the same amount, move the whole stroke.

**Two weights where one is intended.** Set every stroke in the minority tier to the main weight. For an outlined
stroke, move both edges by half the difference so the centre line stays put. For rings, change the outer radius,
the hole radius, or both, keeping the centre.

**Uneven gap between parallel strokes.** Find why the edges are not parallel. For straight strokes, align their
angles. For bends, make all arcs in the bend share one centre and set their radii as consecutive offsets: with
stroke `w` and gap `g`, edge radii step by `w` and `g` alternately (for example 60, 100, 140, 180, 220, 260 with
w = g = 40).

**Arcs just off a shared centre.** Move the stray arcs to the shared centre and recompute their radii so they still
meet their straight segments tangentially. If a straight segment then no longer meets the arc, extend or shorten
it; do not bend it.

**Circles that should match.** Pick the most common size (or the one that fits the grid) and set every member to
it. Keep each centre where it is unless it is also off the grid.

**Edges a few degrees off the angle system.** Rotate the edge to the exact angle around the point that must stay
fixed (usually the end that meets another shape). For a terminal cut, recompute both corners: for a stroke of width
`w` cut at 45 degrees, the two corners are offset by `w` along the stroke from each other.

**Near misses in alignment.** Choose the value that matters most (a centre over an edge, the grid over both) and
move the others to it, or move them at least one module away so the offset reads as intended.

**Almost symmetric.** Fix the other items first, then review again. If a difference remains, keep the better half
and rebuild the other by mirroring or rotating it exactly (in code, or with the design tool's transform with
exact values). Check joins along the axis.

**Tight spots.** Widen to at least the usual gap: shorten the stroke that comes too close, move the ring, or
reduce the ring's outer radius if the system allows.

**Stroke that varies when it should not.** Rebuild its edges as exact offsets of one centre line.

**Balance.** Move or resize the heavy part, or accept it if it matches the personality. For avatars and app icons,
shift the whole mark slightly up toward the optical centre.

## 4. Small sizes: the simplified mark

When gaps close below 32 px, make a separate small version rather than spoiling the main one:

1. Keep the idea and the silhouette; drop secondary details (extra traces, small rings, thin accents).
2. Make strokes and gaps at least 1/16 of the height, so they survive at 16 px; 1/12 is safer.
3. Snap the small version to a pixel grid at its main sizes (16, 32, 48) so edges fall on pixel boundaries.
4. Review it on its own with `review.py`, then look at `08-sizes.png`.

## 5. Colour variants

Only with the owner's approval. Use the variant the review proposes, or adjust OKLCH lightness yourself, keeping the
hue. Record each approved variant with its use (for example: "#65a3bb on backgrounds darker than #3a3f47"). Never
silently replace the master colour.

## 6. After the fixes

- Re-run the review with `--baseline` and show the owner the before and after scorecard.
- Do the optical pass by eye and note each deliberate correction, so later reviews do not "fix" it back.
- Export the kit from the fixed master (with the logo-repolish skill if installed): SVG, PDF, PNG in all sizes,
  icons, lockups.
- Update the brand guidelines: master file, grid, weights, colours and variants, clear space, minimum size.

# Fix brief: Demo mark, draft

Measured from `demo-draft.svg`; positions and sizes are in the file's own units.

## For an agent editing the SVG

Edit a copy of `demo-draft.svg` and make only the changes below. Keep the colours, the concept and everything not listed exactly as they are. Keep every shape a filled outline. Save the result as a new file, then run the review again on it with `--baseline review-draft/findings.json` and confirm each item is fixed and nothing else changed.

1. Circles and curves.
   - Circles that are meant to match differ: 22.0/61.9 at 726.0, 180.0; 19.0/63.9 at 280.0, 820.0. Give them all one size.
   - Arcs centred at 600.0, 668.0 sit 8.0 units from the centre 600.0, 660.0 of the arcs next to them. Make them concentric, keeping the radii that give equal gaps.
2. Angles. Set the edge at 639.8, 99.8 to exactly 135 degrees (now 138.0).
3. Gaps and spacing. The gap near 560.0, 569.3 changes from 37.9 to 54.0 units. Make the facing edges parallel; where they are arcs, give them one centre.
4. Stroke weights. Two weights 40.0 and 44.0 differ by 10%: too little to read as a decision. Set the strokes at 44.0 (near 499.7, 500.7; near 257.5, 819.1) to 40.0, or make the difference at least 15 to 20%.
5. Construction grid.
   - The horizontal stroke between y = 158.0 and 202.0 is 44.0 wide; its centre line is on the grid, so correcting its weight puts both edges on the grid.
   - The horizontal stroke between y = 478.1 and 522.0 is 44.0 wide; its centre line is on the grid, so correcting its weight puts both edges on the grid.
   - The horizontal stroke between y = 798.0 and 842.0 is 44.0 wide; its centre line is on the grid, so correcting its weight puts both edges on the grid.
   - The horizontal stroke between y = 896.0 and 936.0 sits 4.0 units off the grid: move it +4.0 units.
   - Move the corner at x = 617.8 to 620 (+2.2 units).
   - Move the arc centre at x = 726.0 to 720 (-6.0 units).
   - Move the arc centre at y = 668.0 to 660 (-8.0 units).
6. Symmetry. The mark is almost symmetric (turn by 180 degrees); the red and blue areas break it. Fix the items above first and review again; if a difference remains, rebuild one half from the other, or make the difference large enough to read as intended.

## For a designer

Please refine this mark (Demo mark, draft). Keep the concept, colours and proportions; these are construction fixes, not a redesign.

- Circles that are meant to match differ: 22.0/61.9 at 726.0, 180.0; 19.0/63.9 at 280.0, 820.0. Give them all one size.
- Arcs centred at 600.0, 668.0 sit 8.0 units from the centre 600.0, 660.0 of the arcs next to them. Make them concentric, keeping the radii that give equal gaps.
- Set the edge at 639.8, 99.8 to exactly 135 degrees (now 138.0).
- The gap near 560.0, 569.3 changes from 37.9 to 54.0 units. Make the facing edges parallel; where they are arcs, give them one centre.
- Two weights 40.0 and 44.0 differ by 10%: too little to read as a decision. Set the strokes at 44.0 (near 499.7, 500.7; near 257.5, 819.1) to 40.0, or make the difference at least 15 to 20%.
- The horizontal stroke between y = 158.0 and 202.0 is 44.0 wide; its centre line is on the grid, so correcting its weight puts both edges on the grid.
- The horizontal stroke between y = 478.1 and 522.0 is 44.0 wide; its centre line is on the grid, so correcting its weight puts both edges on the grid.
- The horizontal stroke between y = 798.0 and 842.0 is 44.0 wide; its centre line is on the grid, so correcting its weight puts both edges on the grid.
- The horizontal stroke between y = 896.0 and 936.0 sits 4.0 units off the grid: move it +4.0 units.
- Move the corner at x = 617.8 to 620 (+2.2 units).
- Move the arc centre at x = 726.0 to 720 (-6.0 units).
- Move the arc centre at y = 668.0 to 660 (-8.0 units).
- The mark is almost symmetric (turn by 180 degrees); the red and blue areas break it. Fix the items above first and review again; if a difference remains, rebuild one half from the other, or make the difference large enough to read as intended.

Please also look at these, and tell us whether you agree:

- Stroke weights. Horizontal parts (40.0) are as heavy as vertical ones (40.0). Horizontals look heavier than verticals of the same width; type designers often draw them 5 to 10% lighter. Optional for a geometric monoline mark.
- Circles and curves. Radii 220.0 and 228.0 (centres 400.0, 340.0 and 600.0, 668.0) differ by a hair: equal by intent?
- Circles and curves. Radii 259.9 and 268.0 (centres 400.0, 340.0 and 600.0, 668.0) differ by a hair: equal by intent?
- Small sizes. Gaps fill in below about 23 px tall, so the 16 to 32 px favicon sizes blur. For favicons and small avatars, consider a simplified version with fewer, wider gaps.
- Colour on backgrounds. #1d5e74 is weak on dark grey, near-black. For dark backgrounds, a lighter version with the same hue, #65a3bb, gives dark grey 4.6:1, near-black 6.9:1. Use it only with the owner's agreement; the one-colour white or black version is the other option.
- Colour on backgrounds. On mid tones (mid grey) no version of the colour is strong. Use the one-colour white or black version there, or keep the logo off mid-tone and busy photo areas.

Deliver a master SVG with outlined shapes on the 20 units grid, in the same colours.

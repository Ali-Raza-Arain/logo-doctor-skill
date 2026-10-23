# Writing the review

The owner will act on what you write, so it has to be clear, ordered and fair. Measurements give it authority;
judgment gives it value.

## Structure

Use this structure, in the user's language. Keep each part short.

```
## Verdict
Two or three sentences: what the mark does well, the one or two things that hold it back, and how much work the
fixes are (small refinements, or a rebuild).

## Strengths (keep)
- <what works, specifically: the idea, the silhouette, the rhythm, the colour on dark>

## Fix first
1. <fault, in plain words>. <evidence: the numbers and the image>. <what to do>.
2. ...

## Consider
- <judgment, with the reason and the trade-off>

## Colour plan
- On <background>: <version> (<contrast>).
- On <background>: <version> (<contrast>).

## Small sizes
- <what happens at 16 to 32 px, and the plan: fine as is, or a simplified version>

## Next steps
- <what you can do now (fix on a copy, export a kit, write a brief), and what needs the owner's decision>
```

## Tone

- **Specific, not general.** "The middle trace is 44 wide; the others are 40" helps. "The weights feel uneven"
  does not.
- **Facts separate from taste.** Say which points are measured faults and which are your judgment.
- **Respectful.** The logo may be the owner's own work. Never call it ugly, amateur or bad. Describe the effect
  ("this gap widens in the lower bend, so the S looks heavier at the bottom") and the fix.
- **Explain terms once.** "Concentric (sharing one centre)", "counter (the enclosed space inside a shape)".
- **Short.** Five well-chosen fixes beat thirty small ones. Group items with one cause (one wrong stroke width
  puts both of its edges off the grid; that is one fix).
- **Point to the image** for every finding, so the owner can see it, not just read it.

## Example

Feedback for the draft demo mark in this skill's repository (`examples/demo-draft.svg`):

```
## Verdict
A strong, clear idea: an S drawn as three parallel circuit traces with ring ends. The silhouette reads at a glance
and the 45 degree cuts give it a precise, technical character. What holds it back is construction: the lower bowl
is not built from the same centre as the rest, and a few sizes differ by small amounts. All of it is fixable in
the geometry without changing the design.

## Strengths (keep)
- One idea, executed simply: three traces, two rings, one angle system.
- Even rhythm in the upper half: stroke 40, gap 40.
- It turns into itself when rotated by 180 degrees, which makes it feel balanced.

## Fix first
1. Lower bowl: the arcs of the outer trace are centred 8 units below the others (04-circles.png), so the gap
   widens from 38 to 54 (03-gaps.png). Centre them on 600, 660 with radii 220 and 260.
2. Weights: the middle trace and the lower ring are 44 to 45 wide, the rest 40 (02-strokes.png). Set them to 40.
3. Rings: 22 / 62 at the top, 19 / 64 at the bottom. Make both 22 / 62.
4. The top cut is 42 degrees, the others 45 (05-angles.png).
5. The top ring sits 6 units right of the grid (01-grid.png): move it to x = 720.
After these, the mark will be exactly symmetric again (06-symmetry.png shows where it breaks now).

## Consider
- Below about 23 px the gaps fill in (08-sizes.png). For a 16 px favicon, a simplified S with two traces and no
  rings would stay clear.

## Colour plan
- On white and light grey: #1d5e74 as is (7.2:1 and 5.0:1).
- On dark backgrounds it fades (1.8:1 on dark grey). Proposed: #65a3bb, the same hue lighter (4.6:1 and 6.9:1),
  or the white one-colour version. Your decision.

## Next steps
- I can apply fixes 1 to 5 on a copy and show you the before and after scorecard.
```

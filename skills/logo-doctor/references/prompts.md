# Prompts and briefs

Ready-to-use texts. Fill the parts in angle brackets; delete what does not apply. Keep the owner's logo local: never
paste or upload it into an online tool unless the owner explicitly allows it.

## Contents

1. [Asking for a review](#1-asking-for-a-review)
2. [Fixing a logo with an agent](#2-fixing-a-logo-with-an-agent)
3. [Brief for a designer](#3-brief-for-a-designer)
4. [Brief for a new mark](#4-brief-for-a-new-mark)
5. [Exploring concepts with an image tool](#5-exploring-concepts-with-an-image-tool)
6. [Rebuilding a raster logo as clean geometry](#6-rebuilding-a-raster-logo-as-clean-geometry)
7. [Asking people for feedback](#7-asking-people-for-feedback)

## 1. Asking for a review

For a user talking to an agent that has this skill:

```
Review our logo <path/to/logo.svg> like a senior identity designer.
We are <what the business does> for <audience>. It is used on <website, app icon, social avatars, print, signage>.
Our backgrounds are <#hex light> and <#hex dark>. Official colours: <#hex, #hex>.
Measure the construction, check colour on our backgrounds, and give me a prioritised list:
what to fix, what to consider, and what to keep. Do not change the file.
```

## 2. Fixing a logo with an agent

`review.py` writes `fix-brief.md` with the measured items filled in. Its structure, for writing one by hand:

```
Edit a copy of <logo.svg>; coordinates are in the SVG's own units.
Make only these changes. Keep the colours, the concept and everything not listed exactly as it is.
Keep every shape a filled outline. Save the result as <logo-v2.svg>.

1. <The arcs centred at 600, 668 sit 8 units off the shared centre 600, 660: make them concentric, keeping
   the radii that give equal 40-unit gaps.>
2. <Set the strokes measured at 44 to 40, keeping their centre lines.>
3. <Move the ring centre at x = 726 to 720.>

Then run: review.py logo-v2.svg --out review-2 --baseline review-1/findings.json
and confirm each item is fixed and nothing else changed. Report the before and after scorecard.
```

Tips: name every position with coordinates, say what must not change, and ask for verification. An agent given a
vague instruction ("clean up the logo") will change things you wanted kept.

## 3. Brief for a designer

```
Project: construction refinement of the <Brand> logo. Not a redesign.

Keep: the concept, the colours (<#hex>), the overall proportions.
Fix (measured from the master SVG, units are the file's coordinates):
- <item with numbers>
- <item with numbers>
Consider and advise:
- <optical point, small-size version, colour variant for dark backgrounds>

Deliver:
- master SVG with outlined shapes on a grid of <module> units, no transforms, same colours
- a simplified version for 16 to 32 px, if you agree it is needed
- a note of every optical correction you applied, and why
```

## 4. Brief for a new mark

```
Business: <what you do, in one sentence>. Audience: <who buys, and what they care about>.
Competitors: <three to five names>. What they look like: <colours, styles you see in the category>.
Personality, in three words: <precise, calm, senior>.
Name to appear: <name>, set in <font, or "propose one">.
Used on: <website header, app icon, social avatars, print, signage, merchandise>.
Must have: <for example: work in one colour, read at 16 px>.
Must avoid: <for example: gears, globes, swooshes, gradients, the colours of competitor X>.
Deliver: two or three directions, each with its idea in one sentence, shown in context and in one colour.
Construction: on a grid, one or two stroke weights, a small set of radii, exact angles.
```

## 5. Exploring concepts with an image tool

Image generators are useful for loose exploration, not for final logos: they draw pixels with uneven geometry,
can echo existing marks, and in several countries their output may not be protected by copyright without
substantial human authorship. Use them for ideas, then redraw the chosen idea as exact vectors and review it.

Do not upload the owner's existing logo to an online generator without the owner's explicit permission.

```
Flat vector logo mark, <idea in a few words, for example: the letter S formed by three parallel lines with small
ring ends, like circuit traces>. Geometric construction, uniform line weight, exact 45 degree angles, concentric
curves, generous spacing. One colour, <colour name>, on a plain white background. No text, no gradients, no
shadows, no 3D, no texture, no mockup. Centred, with empty space around it.
```

Ask for several variations, pick ideas, not finished artwork. Then build the chosen idea on a grid (see
`fixing.md`, section 2) and run `review.py`.

## 6. Rebuilding a raster logo as clean geometry

For an agent with the logo-repolish skill installed:

```
Rebuild <logo.png> as a precise vector with the logo-repolish skill: exact straight lines on the 45 degree system,
true circles, concentric curves. Keep the colours. Compare the result with the source and show me the difference
image. Then run the logo-doctor review on the new SVG and list what to fix.
```

## 7. Asking people for feedback

Opinions are most useful when the questions are specific and the answers are not led. Show the mark without
explaining it first.

```
1. What kind of company do you think this is?
2. Three words that describe how it feels.
3. Look away for ten seconds, then sketch it from memory.
4. Is anything about it confusing or uncomfortable?
5. Which of these two versions reads better at this size? (show a small version)
```

Ask five to ten people from the target audience, not only colleagues, and look for patterns rather than single
opinions.

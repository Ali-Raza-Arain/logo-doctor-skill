# Colour

How to choose logo colours, and how to make one logo work on light, dark, mid-tone and photographic backgrounds,
for colour-blind viewers and in print.

## Contents

1. [Lightness before hue](#1-lightness-before-hue)
2. [Choosing colours](#2-choosing-colours)
3. [Contrast targets](#3-contrast-targets)
4. [Light, dark and mid-tone backgrounds](#4-light-dark-and-mid-tone-backgrounds)
5. [Colour vision and greyscale](#5-colour-vision-and-greyscale)
6. [Print and special finishes](#6-print-and-special-finishes)
7. [Reading the review's colour sheets](#7-reading-the-reviews-colour-sheets)

## 1. Lightness before hue

Whether a logo is seen depends mostly on the difference in lightness between the logo and its background, not
on hue. A red and a green of the same lightness blur together in greyscale and for many colour-blind viewers. So
decide the lightness first (dark mark on light, or light mark on dark), then the hue.

Work in OKLCH (lightness, chroma, hue), which matches perception far better than RGB or HSL: changing only L keeps
the colour recognisably the same while making it lighter or darker. `review.py` reports each colour in OKLCH.

## 2. Choosing colours

1. **Start from meaning and category.** Look at the main competitors' colours. Owning a colour that nobody else in
   the category uses is worth more than picking the "right" meaning.
2. **Limit the count.** One or two colours for the mark. Each extra colour costs in print, embroidery and small
   sizes, and the logo must work in one colour anyway.
3. **Pick the main background.** Most logos live on white or the brand's own dark colour. Choose the logo colour
   so it reaches at least 3:1 (better 4.5:1) on that background.
4. **Plan the second background now.** A mid-lightness colour that works on both white and black is rare. Decide
   which background the main colour is for, and plan a variant for the other (section 4).
5. **Avoid trend signals** if the mark should last: neon, purple-to-cyan gradients, glow effects and acid green date
   quickly. Classic, restrained colours (navy, deep green, oxblood, graphite, warm neutrals, a considered gold) age
   well.
6. **Check it in context:** website header, dark mode, avatar circle, printed letterhead, signage.

## 3. Contrast targets

The review uses the WCAG 2 contrast ratio (1:1 is identical, 21:1 is black on white).

| Ratio | Grade in the review | Meaning |
| --- | --- | --- |
| 4.5:1 or more | good | Clear at any size, including small icons. |
| 3:1 to 4.5:1 | enough | Clear for a logo of normal size; WCAG asks 3:1 for graphics needed to understand content. |
| under 3:1 | weak | Fades; use a variant or the one-colour version on this background. |

WCAG exempts logos from its contrast rules, so these are design targets, not legal requirements.

## 4. Light, dark and mid-tone backgrounds

- **Dark backgrounds.** A colour chosen for white is often too dark for dark grounds. Make a lighter version with
  the same hue: raise OKLCH lightness until it reaches the target, and reduce chroma a little if it starts to
  glow. The review proposes one (keeping hue and chroma) and shows it in `09-colour-backgrounds.png`.
- **Light backgrounds.** A colour chosen for dark grounds (a light gold, a pale blue) is often too light for
  white. Make a darker version the same way.
- **Gold, yellow and orange** are bright but light: often weak on white and strong on dark. A deeper gold or
  bronze is the usual light-background version.
- **Mid tones** (mid grey, saturated brand colours, photographs) defeat most colours. Use the one-colour white or
  black version, whichever contrasts more, or place the logo on a plain panel.
- **Photographs.** Place the logo over a calm, even area, or on a panel. Never rely on the colour logo over a busy
  image.
- **Irradiation.** A light logo on dark looks bolder than the same logo dark on light. Check thin strokes in the
  dark version at small sizes.
- **Owner's approval.** Variants change the logo's colour, so they are proposals. Present them with the contrast
  numbers and let the owner decide; record approved variants in the brand guidelines.

## 5. Colour vision and greyscale

About 1 in 12 men and 1 in 200 women have a colour vision deficiency, most often red-green (protanopia and
deuteranopia). Tritanopia (blue-yellow) is rare.

- A single-colour logo is safe if its lightness contrast is good; check the dark tiles in the simulation sheet.
- In a multi-colour logo, parts that differ only by hue (red and green, or blue and purple) may merge. Separate
  them by lightness too.
- Greyscale shows the lightness structure: photocopies, fax-like prints, some newspapers and e-paper show it this
  way. Each colour should become a distinctly different grey.

`10-colour-vision.png` simulates protanopia, deuteranopia and tritanopia (Machado, Oliveira and Fernandes, 2009)
and greyscale, on white and near-black.

## 6. Print and special finishes

- **Screen colours do not print the same.** Give the printer the hex values and ask for a proof. For consistent
  results across printers, match a spot colour (such as a Pantone colour) and record it with CMYK and RGB
  equivalents in the guidelines.
- **Metallics** (gold, silver, copper) are printed with foil or metallic ink; on screens they are shown as a flat
  colour or a restrained gradient. Define both.
- **One-colour versions** are needed for embossing, engraving, stamps, embroidery (where very thin strokes fail)
  and fax-like reproduction.

## 7. Reading the review's colour sheets

- `09-colour-backgrounds.png`: the logo on white, off-white, light grey, mid grey, dark grey, near-black and any
  backgrounds passed with `--bg`, each with its contrast ratio and grade. Below, the suggested lighter and darker
  versions on the backgrounds where the original is weak.
- `10-colour-vision.png`: the logo as seen with normal vision, the three colour vision deficiencies and in
  greyscale, on white and near-black.

When you report, name the backgrounds the brand actually uses, give the ratio on each, and state the plan: which
version goes on which background.

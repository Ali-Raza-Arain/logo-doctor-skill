# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Colour checks: how the logo reads on light, mid and dark backgrounds, for people with colour vision deficiencies,
and in greyscale; plus suggested lighter or darker versions of the logo colour for backgrounds where it is weak.

Contrast is the WCAG 2 contrast ratio. WCAG asks 3:1 for graphics needed to understand content (success criterion
1.4.11) and exempts logos, but 3:1 is still the practical floor for a mark to be seen clearly; 4.5:1 is comfortable.
Suggestions keep the hue and chroma of the original colour (in OKLCH) and change only its lightness. They are
proposals for the owner, never applied automatically.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from common import contrast, delta_ok, font, from_oklch, hex_to_rgb, luminance, oklch, simulate, simulate_image

BACKGROUNDS = [('white', '#ffffff'), ('off-white', '#f4f1ea'), ('light grey', '#d4d7dc'), ('mid grey', '#7d828a'),
               ('dark grey', '#2e3238'), ('near-black', '#0b0e13')]
VISION = ['protanopia', 'deuteranopia', 'tritanopia', 'greyscale']


def grade(c):
    return 'good' if c >= 4.5 else ('enough' if c >= 3 else 'weak')


def shift_lightness(colour, bg, target=4.5):
    """Same hue and chroma, lightness moved away from the background until the contrast reaches the target."""
    L, C, H = oklch(colour)
    lighter = luminance(bg) < 0.25
    best = colour
    for i in range(1, 200):
        L2 = L + (0.005 * i if lighter else -0.005 * i)
        if not 0 <= L2 <= 1:
            break
        cand = from_oklch(L2, C, H)
        best = cand
        if contrast(cand, bg) >= target:
            return cand
    return best


def analyse(logo, extra=()):
    bgs = BACKGROUNDS + [(name, hx) for name, hx in extra]
    ink = sum(a.sum() for _, a in logo.layers) or 1
    cols = [{'hex': c, 'share': float(a.sum() / ink), 'oklch': oklch(c)} for c, a in logo.layers]
    table = []
    for name, bg in bgs:
        row = {'bg': name, 'hex': bg, 'contrast': {c['hex']: contrast(c['hex'], bg) for c in cols}}
        row['min'] = min(row['contrast'].values())
        row['grade'] = grade(row['min'])
        table.append(row)
    # suggestions: one darker version for light backgrounds and one lighter version for dark ones
    suggestions = []
    for c in cols:
        for side, rows in (('dark', [r for r in table if luminance(r['hex']) < 0.1]),
                           ('light', [r for r in table if luminance(r['hex']) >= 0.4])):
            weak = [r for r in rows if r['contrast'][c['hex']] < 3]
            if not weak:
                continue
            hardest = min(weak, key=lambda r: r['contrast'][c['hex']]) if side == 'light' else \
                max(weak, key=lambda r: luminance(r['hex']))
            v = shift_lightness(c['hex'], hardest['hex'])
            suggestions.append({'colour': c['hex'], 'side': side, 'variant': v, 'for': [r['bg'] for r in weak],
                                'contrast': {r['bg']: contrast(v, r['hex']) for r in rows}})
    # colour vision and greyscale
    vision = []
    for kind in VISION:
        sim = {c['hex']: simulate(c['hex'], kind) for c in cols}
        entry = {'kind': kind, 'colours': sim, 'on': {}}
        for name, bg in (('white', '#ffffff'), ('near-black', '#0b0e13')):
            sbg = simulate(bg, kind)
            entry['on'][name] = min(contrast(sim[c['hex']], sbg) for c in cols)
        pairs = []
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                a, b = cols[i]['hex'], cols[j]['hex']
                pairs.append({'a': a, 'b': b, 'normal': delta_ok(a, b), 'seen': delta_ok(sim[a], sim[b])})
        entry['pairs'] = pairs
        vision.append(entry)
    merges = [(v['kind'], p) for v in vision for p in v['pairs'] if p['seen'] < 0.06 and p['normal'] >= 0.1]
    lightness_pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a, b = cols[i]['hex'], cols[j]['hex']
            lightness_pairs.append({'a': a, 'b': b, 'contrast': contrast(a, b)})
    mid = [r for r in table if 0.1 <= luminance(r['hex']) < 0.4 and r['grade'] == 'weak']
    return {'colours': cols, 'table': table, 'suggestions': suggestions, 'vision': vision, 'merges': merges,
            'between': lightness_pairs, 'weak_mid': [r['bg'] for r in mid]}


# ---------------------------------------------------------------- sheets

def tile(logo, bg, size=300, recolour=None, margin=0.14):
    """The logo on a background, from the analysis layers (so a suggested colour can be swapped in)."""
    x0, y0, x1, y1 = logo.bbox_px
    side = max(x1 - x0, y1 - y0)
    m = int(side * margin)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    half = side // 2 + m
    out = np.ones((2 * half, 2 * half, 3)) * np.array(hex_to_rgb(bg), float)
    H, W = logo.alpha.shape
    sy0, sx0 = max(0, cy - half), max(0, cx - half)
    sy1, sx1 = min(H, cy + half), min(W, cx + half)
    for c, a in logo.layers:
        col = np.array(hex_to_rgb((recolour or {}).get(c, c)), float)
        aa = np.zeros((2 * half, 2 * half))
        aa[sy0 - (cy - half):sy1 - (cy - half), sx0 - (cx - half):sx1 - (cx - half)] = a[sy0:sy1, sx0:sx1]
        out = out * (1 - aa[..., None]) + col * aa[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).resize((size, size), Image.LANCZOS)


def _label(d, xy, lines, size=19, colour=(30, 30, 30)):
    for i, s in enumerate(lines):
        d.text((xy[0], xy[1] + i * int(size * 1.35)), s, fill=colour, font=font(size))


def backgrounds_sheet(logo, result, path, size=260):
    rows = [('As it is', None, result['table'])]
    for s in result['suggestions']:
        rows.append((f'Suggested {s["side"]}-background version {s["variant"]}', {s['colour']: s['variant']},
                     [r for r in result['table'] if r['bg'] in s['contrast']]))
    cols = len(result['table'])
    W = 20 + cols * (size + 20)
    row_h = size + 100
    sheet = Image.new('RGB', (W, 20 + len(rows) * (row_h + 40)), (246, 246, 246))
    d = ImageDraw.Draw(sheet)
    y = 20
    for title, recolour, items in rows:
        _label(d, (20, y), [title], size=22)
        y += 36
        for i, r in enumerate(items):
            x = 20 + i * (size + 20)
            sheet.paste(tile(logo, r['hex'], size, recolour), (x, y))
            cs = [contrast((recolour or {}).get(c, c), r['hex']) for c in logo.colours]
            c = min(cs)
            colour = (20, 120, 70) if c >= 4.5 else ((170, 110, 0) if c >= 3 else (200, 30, 40))
            _label(d, (x, y + size + 8), [f'{r["bg"]} {r["hex"]}', f'{c:.1f}:1 {grade(c)}'], colour=colour)
        y += row_h
    sheet.save(path, optimize=True)
    return path


def vision_sheet(logo, result, path, size=220):
    kinds = [('normal vision', None)] + [(k, k) for k in VISION]
    bgs = [('white', '#ffffff'), ('near-black', '#0b0e13')]
    W = 220 + len(bgs) * (size + 20)
    sheet = Image.new('RGB', (W, 60 + len(kinds) * (size + 20)), (246, 246, 246))
    d = ImageDraw.Draw(sheet)
    for j, (name, _) in enumerate(bgs):
        _label(d, (220 + j * (size + 20), 18), [f'on {name}'], size=21)
    for i, (label, kind) in enumerate(kinds):
        y = 60 + i * (size + 20)
        _label(d, (20, y + size // 2 - 12), [label], size=21)
        for j, (_, bg) in enumerate(bgs):
            t = tile(logo, bg, size)
            sheet.paste(simulate_image(t, kind) if kind else t, (220 + j * (size + 20), y))
    sheet.save(path, optimize=True)
    return path

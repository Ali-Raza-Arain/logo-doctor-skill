# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Full construction and colour review of a logo, with annotated images, a scorecard and a fix brief.

Usage:
  python review.py logo.svg --out review/ [--name Brand] [--snap 45] [--grid 20] [--grid-origin 0,0]
                   [--bg "brand navy=#0e1f38"] [--colours "#1d5e74,#e0a030"] [--baseline old/findings.json]

Writes into --out (a new or empty folder):
  report.md        scorecard, what to fix first, what to consider, and every measurement
  fix-brief.md     ready-to-use instructions for an agent or a designer, from the findings
  findings.json    the numbers, for comparing a later version with --baseline
  01-grid.png ... 10-colour-vision.png   one annotated image per check

An SVG is measured in its own user units; a raster in its source pixels. SVG gives far more precise results.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colours as C  # noqa: E402
import measure as M  # noqa: E402
from common import (AMBER, BLUE, GREEN, GREY, RED, Canvas, Renderer, add_caption, font, load_logo,  # noqa: E402
                    safe_output_dir)

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('logo')
ap.add_argument('--out', required=True)
ap.add_argument('--name', help='brand or file name for the report title')
ap.add_argument('--snap', type=float, default=45, help='angle step of the design, in degrees (0: no angle system)')
ap.add_argument('--grid', type=float, help='the construction grid module, if known (default: detect)')
ap.add_argument('--grid-origin', default='0,0')
ap.add_argument('--bg', action='append', default=[], help='extra background "name=#hex", repeatable')
ap.add_argument('--colours', help='official logo colours, comma-separated (default: read from the file)')
ap.add_argument('--baseline', help='findings.json of an earlier review, to show what changed')
ap.add_argument('--force', action='store_true')
args = ap.parse_args()

OUT = safe_output_dir(args.out, args.force)
NAME = args.name or Path(args.logo).stem
ORIGIN = tuple(float(v) for v in args.grid_origin.split(','))
EXTRA = [tuple(b.split('=', 1)) for b in args.bg]
t0 = time.time()


def is_in(item, items):
    return any(item is x for x in items)


def n1(v):
    return f'{v:.1f}'


def pct(v):
    return f'{v * 100:.0f}%'


checks = []


def plural(n, one, many=None):
    return f'{n} {one if n == 1 else (many or one + "s")}'


def check(key, title, status, summary, details=(), image=None, fixes=(), consider=(), data=None):
    checks.append({'key': key, 'title': title, 'status': status, 'summary': summary, 'details': list(details),
                   'image': image, 'fixes': [f[0] if isinstance(f, tuple) else f for f in fixes],
                   'consider': list(consider), 'data': data or {}})


with Renderer() as R:
    logo = load_logo(args.logo, R, colours=args.colours.split(',') if args.colours else None)
U = logo.unit_name
st = M.strokes(logo)
gp = M.gaps(logo, st['main'])
ol = M.outline(logo)
ci = M.circles(logo, ol['arcs'])
an = M.angles(ol['lines'], logo.size_px, args.snap, raster=logo.kind != 'svg')
xs, ys = M.key_positions(logo, ol, ci)
gr = M.grid(logo, xs, ys, args.grid, ORIGIN)
al = M.alignment(logo, xs, ys, gr)
sy = M.symmetry(logo)
ba = M.balance(logo)
cx = M.complexity(logo, ol, ci)
co = C.analyse(logo, EXTRA)
W_, H_ = logo.bbox[2] - logo.bbox[0], logo.bbox[3] - logo.bbox[1]
main = st['main']

# ---------------------------------------------------------------- 1. grid and alignment
cv = Canvas(logo)
if gr['module']:
    u = gr['module']
    x_lo, y_lo = logo.x0, logo.y0
    x_hi, y_hi = logo.x0 + logo.alpha.shape[1] / logo.k, logo.y0 + logo.alpha.shape[0] / logo.k
    for axis, lo, hi in (('x', x_lo, x_hi), ('y', y_lo, y_hi)):
        o = gr['origin'][0] if axis == 'x' else gr['origin'][1]
        n0 = int(np.ceil((lo - o) / u))
        for n in range(n0, int((hi - o) / u) + 1):
            v = o + n * u
            major = n % 5 == 0
            a = cv.u(v, y_lo) if axis == 'x' else cv.u(x_lo, v)
            b = cv.u(v, y_hi) if axis == 'x' else cv.u(x_hi, v)
            cv.line(a, b, (232, 51, 109, 200) if major else (120, 170, 230, 110), 2 if major else 1)
            if major:
                cv.text((a[0] + 4, 4) if axis == 'x' else (4, a[1] + 2), f'{v:.4g}', (232, 51, 109), 17)
points = {}
for v, axis, what, at in gr.get('positions', []):
    off = next((o for o in gr['off'] if o['axis'] == axis and abs(o['value'] - v) < 1e-6), None)
    points.setdefault((round(at[0], 2), round(at[1], 2)), []).append((axis, v, off))
for at, items in points.items():
    x, y = cv.u(*at)
    offs = [(axis, v, o) for axis, v, o in items if o]
    if offs:
        cv.d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=RED, width=3)
        cv.text((x + 12, y - 12), ', '.join(f'{axis} {n1(v)}: {o["offset"]:+.1f}' for axis, v, o in offs), RED[:3], 19)
    elif gr['module']:
        cv.d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=GREEN)
for m in al['misses']:
    for v in [g[0] for g in m['members']]:
        a = cv.u(v, logo.bbox[1]) if m['axis'] == 'x' else cv.u(logo.bbox[0], v)
        b = cv.u(v, logo.bbox[3]) if m['axis'] == 'x' else cv.u(logo.bbox[2], v)
        cv.dashed(a, b, AMBER, 2)
img1 = cv.save(OUT / '01-grid.png', [
    f'Grid: {gr["module"]:.4g} {U} module, {pct(gr["coverage"])} of key positions on it.' if gr['module'] else
    'Grid: no single module explains the key positions.',
    'Green: edge, centre or corner on the grid. Red: off the grid, with its offset. Dashed amber: almost aligned.'])
if gr['module']:
    off = gr['off']
    det = [f'Module {gr["module"]:.4g} {U} from origin {gr["origin"][0]:.4g}, {gr["origin"][1]:.4g}; the mark is '
           f'{n1(gr["cells"][0])} by {n1(gr["cells"][1])} modules. {len(gr["positions"]) - len(off)} of '
           f'{len(gr["positions"])} key positions are on it (tolerance {gr["tol"]:.2f} {U}).']
    det += [f'- {o["what"]} at {o["axis"]} = {n1(o["value"])}: {o["offset"]:+.1f} {U} from the grid line {o["grid"]:.4g}'
            for o in off]
    # Two edges of one stroke, both off: either the stroke is the wrong width (offsets opposite) or the whole
    # stroke sits in the wrong place (offsets equal). One fix each, not two.
    widths = [sg['width'] for sg in st['segments']] or [main or 0]
    edges = sorted([o for o in off if 'edge' in o['what']], key=lambda o: (o['axis'], o['value']))
    used, fixes = set(), []
    for i, a in enumerate(edges):
        for b in edges[i + 1:]:
            if id(a) in used or id(b) in used or a['axis'] != b['axis']:
                continue
            gap_ab = b['value'] - a['value']
            if not any(abs(gap_ab - w) < max(1.0, 0.03 * w) for w in widths):
                continue
            used.update((id(a), id(b)))
            line = 'horizontal' if a['axis'] == 'y' else 'vertical'
            if abs(a['offset'] + b['offset']) < gr['tol']:
                fixes.append(f'The {line} stroke between {a["axis"]} = {n1(a["value"])} and {n1(b["value"])} is '
                             f'{n1(gap_ab)} wide; its centre line is on the grid, so correcting its weight puts both '
                             'edges on the grid.')
            else:
                fixes.append(f'The {line} stroke between {a["axis"]} = {n1(a["value"])} and {n1(b["value"])} sits '
                             f'{n1(abs(a["offset"]))} {U} off the grid: move it {-a["offset"]:+.1f} {U}.')
    fixes += [f'Move the {o["what"]} at {o["axis"]} = {n1(o["value"])} to {o["grid"]:.4g} ({-o["offset"]:+.1f} {U}).'
              for o in off if id(o) not in used and abs(o['offset']) < gr['module'] / 2]
    check('grid', 'Construction grid', 'Fix' if off else 'Pass',
          f'{len(off)} of {len(gr["positions"])} key positions off the grid of {gr["module"]:.4g} {U}' if off else
          f'every key position sits on a grid of {gr["module"]:.4g} {U}', det, img1.name, fixes,
          data={'module': gr['module'], 'off': len(off), 'positions': len(gr['positions'])})
elif gr.get('too_few'):
    check('grid', 'Construction grid', 'Info', f'only {len(gr["positions"])} key positions, too few to tell a grid',
          ['A grid matters most for marks with many parts. Pass --grid if the mark was built on one.'], img1.name,
          data={'module': None})
else:
    check('grid', 'Construction grid', 'Check', 'no consistent grid found',
          ['No module between 1/150 and 1/6 of the mark explains most key positions. The mark may be drawn by eye, '
           'or traced from a raster. Building it on a grid makes widths, gaps and positions repeatable.'],
          img1.name, consider=['Rebuild the mark on a grid (references/construction.md, section Grid).'],
          data={'module': None})
off_vals = {(o['axis'], round(o['value'], 2)) for o in gr.get('off', [])}
covered = [m for m in al['misses'] if any((m['axis'], round(g[0], 2)) in off_vals for g in m['members'])]
own = [m for m in al['misses'] if not is_in(m, covered)]
if al['misses']:
    det = [f'- {m["axis"]} = ' + ', '.join(f'{n1(g[0])} ({g[1]})' for g in m['members']) +
           f': spread over {n1(m["diff"])} {U}' + (' (resolved by the grid fix)' if is_in(m, covered) else '')
           for m in al['misses']]
    check('alignment', 'Alignment', 'Fix' if own else 'Pass',
          f'{plural(len(own), "group")} of positions almost line up but miss' if own else
          f'{plural(len(covered), "near miss", "near misses")}, already covered by the grid fixes',
          det, img1.name, [f'{len(m["members"])} positions at {m["axis"]} = ' +
                           ', '.join(n1(g[0]) for g in m['members']) +
                           ' nearly line up: align them on one value, or move them clearly apart.' for m in own],
          data={'misses': len(own)})
else:
    check('alignment', 'Alignment', 'Pass', 'no near misses between edges, centres and corners', image=img1.name,
          data={'misses': 0})

# ---------------------------------------------------------------- 2. stroke weights


def sample(rows, cols, spacing):
    keep, cells = [], {}
    for i in range(0, len(rows), 2):
        key = (int(rows[i] // spacing), int(cols[i] // spacing))
        near = [j for dy in (-1, 0, 1) for dx in (-1, 0, 1) for j in cells.get((key[0] + dy, key[1] + dx), [])]
        if all((rows[j] - rows[i]) ** 2 + (cols[j] - cols[i]) ** 2 >= spacing ** 2 for j in near):
            cells.setdefault(key, []).append(i)
            keep.append(i)
    return keep


def tone(dev, ok, warn):
    return GREEN if abs(dev) <= ok else (AMBER if abs(dev) <= warn else RED)


cv = Canvas(logo)
main = st['main']
if st['segments']:
    close_vals = {v for a, b, _, _ in st['close_tiers'] for v in (a, b)}
    for s in st['segments']:
        ref = st['tiers'][s['tier']]['value']
        if ref in close_vals:
            ref = main
        for i in sample(s['rows'], s['cols'], 1.25 * s['width'] * logo.k):
            if s['w'][i] < 0.8 * s['width']:
                continue                                # the narrowing at a cut or rounded end, not the stroke
            cv.circle(s['cols'][i], s['rows'][i], s['w'][i] * logo.k / 2, tone(s['w'][i] / ref - 1, 0.025, 0.06), 2)
        mid = len(s['rows']) // 2
        x, y = cv.p(s['cols'][mid], s['rows'][mid])
        cv.text((x + 6, y - 30), n1(s['width']), (20, 20, 20), 22)
img2 = cv.save(OUT / '02-strokes.png', [
    f'Stroke weights: circles fitted inside every stroke. Main weight {n1(main)} {U}.' if main else 'Stroke weights.',
    'Green: within 2.5% of its weight. Amber: 2.5 to 6% off. Red: more than 6% off.'])
if st['segments']:
    tiers_txt = ', '.join(f'{n1(t["value"])} ({pct(t["share"])} of the stroke length)' for t in st['tiers'])
    det = [f'Weights found: {tiers_txt}.', '', f'| Part near (x, y) | Width ({U}) | 10th to 90th percentile | Length |',
           '| --- | --- | --- | --- |']
    det += [f'| {n1(s["at"][0])}, {n1(s["at"][1])} | {n1(s["width"])} | {n1(s["p10"])} to {n1(s["p90"])} | '
            f'{s["length"]:.0f} |' for s in sorted(st['segments'], key=lambda s: -s['length'])[:20]]
    bk = st['by_kind']
    if bk:
        det += ['', 'Main weight by direction: ' + ', '.join(f'{k_} {n1(v["width"])}' for k_, v in bk.items()) + '.']
    fixes, consider = [], []
    for a, b, sa, sb in st['close_tiers']:
        lo, hi = (a, b) if sa >= sb else (b, a)
        where = '; '.join(f'near {n1(s["at"][0])}, {n1(s["at"][1])}' for s in st['segments']
                          if abs(st['tiers'][s['tier']]['value'] - hi) < 1e-9)
        fixes.append((f'Two weights {n1(a)} and {n1(b)} differ by {pct(b / a - 1)}: too little to read as a decision. '
                      f'Set the strokes at {n1(hi)} ({where}) to {n1(lo)}, or make the difference at least 15 to 20%.',
                      'weights'))
    for s in st['uneven']:
        consider.append(f'The stroke near {n1(s["at"][0])}, {n1(s["at"][1])} varies from {n1(s["p10"])} to '
                        f'{n1(s["p90"])}: intended taper, or edges that should be parallel?')
    if 'horizontal' in bk and 'vertical' in bk and bk['horizontal']['width'] >= 0.99 * bk['vertical']['width']:
        consider.append(f'Horizontal parts ({n1(bk["horizontal"]["width"])}) are as heavy as vertical ones '
                        f'({n1(bk["vertical"]["width"])}). Horizontals look heavier than verticals of the same width; '
                        'type designers often draw them 5 to 10% lighter. Optional for a geometric monoline mark.')
    status = 'Fix' if fixes else ('Check' if st['uneven'] else 'Pass')
    summary = (f'{len(st["tiers"])} weights where one is intended: ' + ' and '.join(n1(t['value']) for t in st['tiers'])
               if fixes else f'consistent: {tiers_txt}')
    check('strokes', 'Stroke weights', status, summary, det, img2.name, fixes, consider,
          data={'tiers': [round(t['value'], 2) for t in st['tiers']], 'main': main})
else:
    check('strokes', 'Stroke weights', 'Info', 'no strokes found to measure (solid shapes only)', image=img2.name)

# ---------------------------------------------------------------- 3. gaps
cv = Canvas(logo)
if gp['channels']:
    usual = gp['usual']
    for c in gp['channels']:
        for i in sample(c['rows'], c['cols'], 1.25 * c['median'] * logo.k):
            w = c['w'][i]
            col = RED if w < gp['floor'] else tone(w / usual - 1, 0.08, 0.2)
            cv.circle(c['cols'][i], c['rows'][i], w * logo.k / 2, col, 2)
        flagged = any(c is x for x in gp['uneven'] + gp['tight'])
        if flagged:
            for v in (c['min'], float(np.max(c['w']))):
                i = int(np.argmin(np.abs(c['w'] - v)))
                x, y = cv.p(c['cols'][i], c['rows'][i])
                cv.text((x + 8, y - 12), n1(v), RED[:3], 22)
        else:
            mid = len(c['rows']) // 2
            x, y = cv.p(c['cols'][mid], c['rows'][mid])
            cv.text((x + 8, y - 12), n1(c['median']), (20, 20, 20), 20)
img3 = cv.save(OUT / '03-gaps.png', [
    f'Gaps: circles fitted between facing edges. Usual gap {n1(gp["usual"])} {U}.' if gp['usual'] else 'Gaps.',
    'Green: within 8% of the usual gap. Amber: 8 to 20% off. Red: further off, or tight.'])
if gp['channels']:
    det = [f'Usual gap {n1(gp["usual"])} {U}; narrowest {n1(gp["narrowest"])}. Gap to stroke ratio '
           f'{gp["usual"] / main:.2f}.' if main else f'Usual gap {n1(gp["usual"])} {U}.']
    det += [f'- Gap near {n1(c["at"][0])}, {n1(c["at"][1])}: median {n1(c["median"])}, from {n1(c["p5"])} to '
            f'{n1(c["p95"])}, length {c["length"]:.0f}' for c in sorted(gp['channels'], key=lambda c: -c['length'])]
    fixes = [(f'The gap near {n1(c["at"][0])}, {n1(c["at"][1])} changes from {n1(c["p5"])} to {n1(c["p95"])} {U}. '
              'Make the facing edges parallel; where they are arcs, give them one centre.', 'gaps')
             for c in gp['uneven']]
    fixes += [(f'Tight spot near {n1(c["min_at"][0])}, {n1(c["min_at"][1])}: {n1(c["min"])} {U}, under '
               f'{n1(gp["floor"])}. Widen it; tight spots close up first at small sizes and in print.', 'gaps')
              for c in gp['tight']]
    check('gaps', 'Gaps and spacing', 'Fix' if fixes else 'Pass',
          ', '.join(t for t in (plural(len(gp['uneven']), 'uneven gap') if gp['uneven'] else '',
                                plural(len(gp['tight']), 'tight spot') if gp['tight'] else '') if t) if fixes else
          f'even: the usual gap is {n1(gp["usual"])} {U}', det, img3.name, fixes,
          data={'usual': gp['usual'], 'uneven': len(gp['uneven']), 'tight': len(gp['tight'])})
else:
    check('gaps', 'Gaps and spacing', 'Info', 'no narrow gaps between parts', image=img3.name)

# ---------------------------------------------------------------- 4. circles, rings and centres
cv = Canvas(logo)
palette = [(40, 110, 230, 230), (22, 150, 90, 230), (150, 60, 200, 230), (0, 150, 170, 230), (200, 120, 0, 230)]
bad_centres = {(round(n['other']['cx'], 2), round(n['other']['cy'], 2)) for n in ci['near_concentric']}
for gi, e in enumerate(ci['centres']):
    off = (round(e['cx'], 2), round(e['cy'], 2)) in bad_centres
    col = RED if off else palette[gi % len(palette)]
    for r in sorted({round(a['r'], 1) for a in e['arcs']}):
        x, y = cv.u(e['cx'], e['cy'])
        rr = r * logo.k * cv.f
        cv.d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col[:3] + (150,), width=2)
    x, y = cv.u(e['cx'], e['cy'])
    cv.line((x - 10, y), (x + 10, y), col, 3)
    cv.line((x, y - 10), (x, y + 10), col, 3)
for r in ci['rings']:
    x, y = cv.u(r['cx'], r['cy'])
    bad = any(r is x for g in ci['mismatched'] for x in g)
    cv.text((x + 14, y + 10), f'{n1(r["r_in"])} / {n1(r["r_out"])}', RED[:3] if bad else (20, 20, 20), 22)
for n in ci['near_concentric']:
    a, b = cv.u(n['ref']['cx'], n['ref']['cy']), cv.u(n['other']['cx'], n['other']['cy'])
    cv.line(a, b, RED, 3)
    cv.text((b[0] + 14, b[1] - 6), f'{n1(n["offset"])} {U} off centre', RED[:3], 22)
img4 = cv.save(OUT / '04-circles.png', [
    'Circles and arcs: every arc drawn as its full circle, with its centre. Arcs that share a centre share a colour.',
    'Rings are labelled hole radius / outer radius. Red: a centre or ring that misses its partner.'])
det = [f'{len(ci["rings"])} rings, {len(ci["dots"])} dots, {len(ci["holes"])} round holes; '
       f'{len(ci["centres"])} distinct arc centres.']
det += [f'- Ring at {n1(r["cx"])}, {n1(r["cy"])}: hole radius {n1(r["r_in"])}, outer radius {n1(r["r_out"])}'
        for r in ci['rings']]
det += [f'- Arc centre {n1(e["cx"])}, {n1(e["cy"])}: radii ' + ', '.join(sorted({n1(a['r']) for a in e['arcs']}, key=float))
        for e in ci['centres'] if not e['ring']]
fixes, consider = [], []
for g in ci['mismatched']:
    vals = '; '.join(f'{n1(r.get("r_in", r.get("r", 0)))}/{n1(r.get("r_out", r.get("r", 0)))} at {n1(r["cx"])}, '
                     f'{n1(r["cy"])}' for r in g)
    fixes.append((f'Circles that are meant to match differ: {vals}. Give them all one size.', 'circles'))
for n in ci['near_concentric']:
    fixes.append((f'Arcs centred at {n1(n["other"]["cx"])}, {n1(n["other"]["cy"])} sit {n1(n["offset"])} {U} from the '
                  f'centre {n1(n["ref"]["cx"])}, {n1(n["ref"]["cy"])} of the arcs next to them. Make them concentric, '
                  'keeping the radii that give equal gaps.', 'concentric'))
for c_ in ci['close_radii']:
    consider.append(f'Radii {n1(c_["r1"])} and {n1(c_["r2"])} (centres {n1(c_["at1"][0])}, {n1(c_["at1"][1])} and '
                    f'{n1(c_["at2"][0])}, {n1(c_["at2"][1])}) differ by a hair: equal by intent?')
if not ci['centres']:
    check('circles', 'Circles and curves', 'Info', 'no circular arcs found', det, img4.name)
else:
    check('circles', 'Circles and curves', 'Fix' if fixes else ('Check' if consider else 'Pass'),
          ', '.join(t for t in (plural(len(ci['mismatched']), 'set') + ' of circles that should match'
                                if ci['mismatched'] else '',
                                plural(len(ci['near_concentric']), 'centre') + ' just off its partner'
                                if ci['near_concentric'] else '') if t)
          if fixes else 'circles match and shared centres are exact', det, img4.name, fixes, consider,
          data={'rings': len(ci['rings']), 'mismatched': len(ci['mismatched']),
                'near_concentric': len(ci['near_concentric'])})

# ---------------------------------------------------------------- 5. angles
cv = Canvas(logo)
for l in an['lines']:
    a, b = cv.u(*l['a']), cv.u(*l['b'])
    off = any(l is x for x in an['off'])
    cv.line(a, b, RED if off else GREEN, 5 if off else 4)
    if off:
        cv.text(((a[0] + b[0]) / 2 + 10, (a[1] + b[1]) / 2 - 10), f'{l["angle"]:.1f} degrees, not {l["snap"]:g}',
                RED[:3], 22)
system = ', '.join(f'{a:g} ({n})' for a, n in an['system'].items())
img5 = cv.save(OUT / '05-angles.png', [
    f'Angles: straight edges, measured. Angle system ({args.snap:g} degree steps): {system}.' if args.snap else
    'Angles: straight edges.', 'Green: exactly on the angle system. Red: close to it but off.'])
det = [f'{len(an["lines"])} straight edges measured. Angles found (0 is horizontal, 90 vertical, y up): {system}.']
det += [f'- Edge at {n1(l["mid"][0])}, {n1(l["mid"][1])}, length {l["length"]:.0f}: {l["angle"]:.2f} degrees, '
        f'{l["dev"]:.2f} off {l["snap"]:g}' for l in an['off']]
fixes = [(f'Set the edge at {n1(l["mid"][0])}, {n1(l["mid"][1])} to exactly {l["snap"]:g} degrees (now '
          f'{l["angle"]:.1f}).', 'angles') for l in an['off']]
check('angles', 'Angles', 'Fix' if fixes else ('Pass' if an['lines'] else 'Info'),
      f'{plural(len(fixes), "edge")} a few degrees off the {args.snap:g} degree system' if fixes else
      (f'every straight edge is on the angle system ({system})' if an['lines'] else 'no long straight edges'),
      det, img5.name, fixes, data={'off': len(an['off']), 'system': {str(k_): v for k_, v in an['system'].items()}})

# ---------------------------------------------------------------- 6. symmetry
cv = Canvas(logo)
bv = sy['variants'][sy['best']]
x0p, y0p = bv['origin']
for mask, col in ((bv['only_here'], (220, 30, 40)), (bv['only_there'], (40, 110, 230))):
    if mask.any():
        full = np.zeros(logo.alpha.shape, bool)
        full[y0p:y0p + mask.shape[0], x0p:x0p + mask.shape[1]] = ndimage.binary_opening(mask, iterations=2)
        small = Image.fromarray((full * 255).astype(np.uint8)).resize(cv.size, Image.BOX)
        tint = Image.new('RGBA', cv.size, col + (255,))
        tint.putalpha(small.point(lambda v: 255 if v > 40 else 0))
        cv.layer = Image.alpha_composite(cv.layer, tint)
        cv.d = ImageDraw.Draw(cv.layer)
mx, my = (logo.bbox[0] + logo.bbox[2]) / 2, (logo.bbox[1] + logo.bbox[3]) / 2
if 'left to right' in sy['best']:
    cv.dashed(cv.u(mx, logo.bbox[1]), cv.u(mx, logo.bbox[3]), GREY, 2)
elif 'top to bottom' in sy['best']:
    cv.dashed(cv.u(logo.bbox[0], my), cv.u(logo.bbox[2], my), GREY, 2)
else:
    x, y = cv.u(mx, my)
    cv.d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=GREY)
img6 = cv.save(OUT / '06-symmetry.png', [
    f'Symmetry, {sy["best"]}: the mark compared with its own {"rotation" if "turn" in sy["best"] else "mirror image"}.',
    'Red: ink only in the mark. Blue: ink only in the transformed copy. None at all means exact symmetry.'])
det = [f'- {name}: {v["verdict"]}; largest difference {n1(v["max_dev"])} {U}; overlap {pct(v["iou"])}'
       for name, v in sy['variants'].items()]
if bv['verdict'] == 'nearly':
    check('symmetry', 'Symmetry', 'Fix', f'almost symmetric ({sy["best"]}), but parts differ by up to '
          f'{n1(bv["max_dev"])} {U}', det, img6.name,
          [f'The mark is almost symmetric ({sy["best"]}); the red and blue areas break it. Fix the items above '
           'first and review again; if a difference remains, rebuild one half from the other, or make the difference '
           'large enough to read as intended.'],
          data={'best': sy['best'], 'verdict': 'nearly', 'max_dev': bv['max_dev']})
elif bv['verdict'] == 'symmetric':
    check('symmetry', 'Symmetry', 'Pass', f'exactly symmetric ({sy["best"]})', det, img6.name,
          data={'best': sy['best'], 'verdict': 'symmetric'})
else:
    check('symmetry', 'Symmetry', 'Info', 'not symmetric, by design', det, img6.name,
          data={'best': sy['best'], 'verdict': 'no'})

# ---------------------------------------------------------------- 7. balance
cv = Canvas(logo)
bx0, by0 = cv.u(logo.bbox[0], logo.bbox[1])
bx1, by1 = cv.u(logo.bbox[2], logo.bbox[3])
for a, b in (((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))):
    cv.dashed(a, b, GREY, 2)
cxp, cyp = cv.u(*ba['centre'])
cv.dashed((cxp, by0), (cxp, by1), GREY, 1)
cv.dashed((bx0, cyp), (bx1, cyp), GREY, 1)
gx, gy = cv.u(*ba['centroid'])
cv.d.ellipse((gx - 10, gy - 10, gx + 10, gy + 10), fill=RED)
for name, (qx, qy) in {'top left': (bx0, by0), 'top right': (cxp, by0), 'bottom left': (bx0, cyp),
                       'bottom right': (cxp, cyp)}.items():
    cv.text((qx + 12, qy + 10), pct(ba['quadrants'][name]), (60, 60, 60), 24)
img7 = cv.save(OUT / '07-balance.png', [
    'Balance: red dot is the centre of the ink, the crossing lines the centre of the bounding box.',
    'Percentages: share of the ink in each quarter.'])
det = [('The centre of the ink sits on the centre of the box. ' if max(abs(ba['dx']), abs(ba['dy'])) < 0.005 else
        f'Centre of ink is {pct(abs(ba["dx"]))} of the width {"right" if ba["dx"] > 0 else "left"} and '
        f'{pct(abs(ba["dy"]))} of the height {"above" if ba["dy"] > 0 else "below"} the box centre. ') +
       f'Top half {pct(ba["top"])}, left half {pct(ba["left"])}. Ink covers {pct(ba["ink_share"])} of the box.']
consider = []
if abs(ba['dx']) > 0.03:
    consider.append(f'The weight sits {pct(abs(ba["dx"]))} to the {"right" if ba["dx"] > 0 else "left"}: intended?')
if ba['dy'] > 0.03:
    consider.append(f'The weight sits {pct(ba["dy"])} above centre, so the mark may look top-heavy. Marks usually '
                    'feel stable with their weight at or slightly below the optical centre, which is a little above '
                    'the geometric one.')
check('balance', 'Balance', 'Check' if consider else 'Pass',
      'weight off centre' if consider else 'the visual weight is centred', det, img7.name, consider=consider,
      data={'dx': ba['dx'], 'dy': ba['dy']})

# ---------------------------------------------------------------- 8. small sizes, blur and silhouette
sizes = [16, 24, 32, 48, 64, 128]
tiles = []
for bg in ('#ffffff', '#0b0e13'):
    row = []
    for s in sizes:
        t = C.tile(logo, bg, s, margin=0.06)
        row.append((s, t.resize((s * 4 if s < 128 else s * 2,) * 2, Image.NEAREST)))
    tiles.append(row)
big = C.tile(logo, '#ffffff', 300, margin=0.1)
blur = big.filter(ImageFilter.GaussianBlur(300 * 0.025))
sil_mask = ndimage.binary_fill_holes(logo.mask)
sil = Image.fromarray(np.where(sil_mask, 30, 255).astype(np.uint8)).convert('RGB')
x0p, y0p, x1p, y1p = logo.bbox_px
side = max(x1p - x0p, y1p - y0p)
pad = int(side * 0.1)
box = Image.new('RGB', (side + 2 * pad, side + 2 * pad), (255, 255, 255))
box.paste(sil, (side // 2 + pad - (x0p + x1p) // 2, side // 2 + pad - (y0p + y1p) // 2))
sil = box.resize((300, 300), Image.LANCZOS)
row_w = sum(t.width + 20 for _, t in tiles[0]) + 20
sheet = Image.new('RGB', (max(row_w, 1000), 2 * (256 + 60) + 400), (246, 246, 246))
d = ImageDraw.Draw(sheet)
y = 20
for row in tiles:
    x = 20
    for s, t in row:
        d.text((x, y), f'{s} px', fill=(40, 40, 40), font=font(18))
        sheet.paste(t, (x, y + 26))
        x += t.width + 20
    y += 256 + 60
for i, (label, im) in enumerate((('Blur test (squint)', blur), ('Silhouette', sil), ('Full size', big))):
    d.text((20 + i * 330, y), label, fill=(40, 40, 40), font=font(20))
    sheet.paste(im, (20 + i * 330, y + 30))
sheet.save(OUT / '08-sizes.png', optimize=True)
thin = min([s['width'] for s in st['segments']] or [main or 1])
narrow = gp.get('narrowest') or None
height_u = H_
det = [f'Thinnest stroke {n1(thin)} {U} ({thin / height_u:.1%} of the height).']
consider = []
if narrow:
    closes = height_u / narrow
    det.append(f'Narrowest gap {n1(narrow)} {U}: under 1 pixel when the mark is shorter than about {closes:.0f} px, '
               'so it fills in there.')
    if closes > 16:
        consider.append(f'Gaps fill in below about {closes:.0f} px tall, so the 16 to 32 px favicon sizes blur. For '
                        'favicons and small avatars, consider a simplified version with fewer, wider gaps.')
if thin / height_u < 0.02:
    consider.append('Strokes under 2% of the height turn faint below about 50 px and swell on dark backgrounds '
                    '(light on dark looks bolder). Check the dark and small tiles.')
check('sizes', 'Small sizes', 'Check' if consider else 'Pass',
      consider[0].split('.')[0] if consider else 'holds up down to favicon sizes', det, '08-sizes.png',
      consider=consider, data={'closes_below_px': (height_u / narrow) if narrow else None})

# ---------------------------------------------------------------- 9 and 10. colour
C.backgrounds_sheet(logo, co, OUT / '09-colour-backgrounds.png')
C.vision_sheet(logo, co, OUT / '10-colour-vision.png')
cols_txt = ', '.join(f'{c["hex"]} ({pct(c["share"])} of the ink; OKLCH {c["oklch"][0]:.2f} {c["oklch"][1]:.3f} '
                     f'{c["oklch"][2]:.0f})' for c in co['colours'])
det = [f'Colours: {cols_txt}.', '', '| Background | Contrast | Grade |', '| --- | --- | --- |']
det += [f'| {r["bg"]} {r["hex"]} | {r["min"]:.1f}:1 | {r["grade"]} |' for r in co['table']]
for v in co['vision']:
    det.append(f'- {v["kind"]}: contrast on white {v["on"]["white"]:.1f}:1, on near-black {v["on"]["near-black"]:.1f}:1')
consider = []
for s in co['suggestions']:
    cs = ', '.join(f'{k_} {v:.1f}:1' for k_, v in s['contrast'].items())
    consider.append(f'{s["colour"]} is weak on {", ".join(s["for"])}. For {s["side"]} backgrounds, a '
                    f'{"lighter" if s["side"] == "dark" else "darker"} version with the same hue, {s["variant"]}, '
                    f'gives {cs}. Use it only with the owner\'s agreement; the one-colour white or black version is '
                    'the other option.')
if co['weak_mid']:
    consider.append(f'On mid tones ({", ".join(co["weak_mid"])}) no version of the colour is strong. Use the '
                    'one-colour white or black version there, or keep the logo off mid-tone and busy photo areas.')
for kind, p in co['merges']:
    consider.append(f'{p["a"]} and {p["b"]} look almost the same with {kind}. Separate them by lightness, not hue.')
for p in co['between']:
    if p['contrast'] < 1.3:
        consider.append(f'{p["a"]} and {p["b"]} have nearly the same lightness ({p["contrast"]:.2f}:1), so they merge '
                        'in greyscale print and photocopies.')
weak = [r['bg'] for r in co['table'] if r['grade'] == 'weak']
check('colour', 'Colour on backgrounds', 'Check' if consider else 'Pass',
      f'weak on {", ".join(weak)}' if weak else 'reads on light, mid and dark backgrounds',
      det, '09-colour-backgrounds.png', consider=consider,
      data={'weak_on': weak, 'suggestions': [s['variant'] for s in co['suggestions']]})
check('vision', 'Colour vision and greyscale', 'Check' if co['merges'] else 'Pass',
      'colours merge for some viewers' if co['merges'] else 'readable with common colour vision deficiencies',
      ['See the simulation sheet: protanopia and deuteranopia (red-green), tritanopia (blue-yellow), greyscale. '
       'About 1 in 12 men and 1 in 200 women have a colour vision deficiency.'], '10-colour-vision.png',
      data={'merges': len(co['merges'])})
check('complexity', 'Complexity', 'Info',
      f'{cx["parts"]} parts, {cx["holes"]} enclosed counters, {cx["lines"]} straight edges, {cx["arcs"]} arcs',
      [f'Edge index {cx["edge_index"]:.1f} (outline length over the square root of the ink area). Simple marks are '
       'often under 15; detailed ones over 30. A higher number is not wrong, but it costs small-size legibility.'],
      data=cx)

# ---------------------------------------------------------------- report
base = {}
if args.baseline:
    base = {c['key']: c['status'] for c in json.loads(Path(args.baseline).read_text())['checks']}
lines = [f'# Logo review: {NAME}', '',
         f'File: `{Path(args.logo).name}` ({logo.kind}). Measured in the file\'s own {U}; the mark is '
         f'{n1(W_)} by {n1(H_)} {U}. Colours: {", ".join(logo.colours)}.', '',
         'Automated measurements find construction faults precisely, but they do not judge intent. Read each item '
         'with the images and decide whether it is a fault or a choice.', '', '## Scorecard', '',
         '| Check | ' + ('Before | ' if base else '') + 'Result | Finding |',
         '| --- | ' + ('--- | ' if base else '') + '--- | --- |']
for c in checks:
    lines.append(f'| {c["title"]} | ' + (f'{base.get(c["key"], "")} | ' if base else '') +
                 f'{c["status"]} | {c["summary"]} |')
ORDER = ['circles', 'angles', 'gaps', 'strokes', 'grid', 'alignment', 'symmetry']
ordered = sorted([c for c in checks if c['fixes']], key=lambda c: ORDER.index(c['key']) if c['key'] in ORDER else 99)
fixes = [(c['title'], f) for c in ordered for f in c['fixes']]
consider = [(c['title'], t) for c in checks for t in c['consider']]


def numbered(items, cap=6):
    out = []
    for i, c in enumerate(items, 1):
        if len(c['fixes']) == 1:
            out.append(f'{i}. **{c["title"]}.** {c["fixes"][0]}')
        else:
            out.append(f'{i}. **{c["title"]}.**')
            out += [f'   - {f}' for f in c['fixes'][:cap]]
            if len(c['fixes']) > cap:
                out.append(f'   - and {len(c["fixes"]) - cap} more of the same kind (see Details).')
    return out


lines += ['', '## Fix first', '', 'In this order: geometry first, then weights and spacing, then positions.', '']
lines += numbered(ordered) or ['Nothing: no construction faults found.']
lines += ['', '## Consider', '']


def considered(cap=4):
    out = []
    for c in checks:
        for t in c['consider'][:cap]:
            out.append(f'- **{c["title"]}.** {t}')
        if len(c['consider']) > cap:
            out.append(f'- **{c["title"]}.** And {len(c["consider"]) - cap} more of the same kind (see Details).')
    return out


lines += considered() or ['Nothing further.']
lines += ['', '## Details']
for c in checks:
    lines += ['', f'### {c["title"]}: {c["status"]}', '', c['summary'][0].upper() + c['summary'][1:] + '.']
    if c['image']:
        lines += ['', f'![{c["title"]}]({c["image"]})']
    if c['details']:
        lines += [''] + c['details']
    if len(c['consider']) > 4:
        lines += ['', 'All points to consider:', ''] + [f'- {t}' for t in c['consider']]
if any(c['key'] == 'vision' for c in checks):
    lines += ['', '![Colour vision](10-colour-vision.png)']
(OUT / 'report.md').write_text('\n'.join(lines) + '\n')

brief = [f'# Fix brief: {NAME}', '',
         f'Measured from `{Path(args.logo).name}`; positions and sizes are in the file\'s own {U}.', '',
         '## For an agent editing the SVG', '',
         f'Edit a copy of `{Path(args.logo).name}` and make only the changes below. Keep the colours, the concept '
         'and everything not listed exactly as they are. Keep every shape a filled outline. Save the result as a new '
         f'file, then run the review again on it with `--baseline {OUT.name}/findings.json` and confirm each item '
         'is fixed and nothing else changed.', '']
brief += [ln.replace('**', '') for ln in numbered(ordered, cap=999)] or ['No construction fixes are needed.']
brief += ['', '## For a designer', '',
          f'Please refine this mark ({NAME}). Keep the concept, colours and proportions; these are construction fixes, '
          'not a redesign.', '']
brief += [f'- {f}' for _, f in fixes] or ['- No construction faults were found.']
if consider:
    brief += ['', 'Please also look at these, and tell us whether you agree:', '']
    brief += [ln.replace('**', '') for ln in considered(cap=999)]
brief += ['', f'Deliver a master SVG with outlined shapes' + (f' on the {gr["module"]:g} {U} grid' if gr['module']
                                                               else '') + ', in the same colours.']
(OUT / 'fix-brief.md').write_text('\n'.join(brief) + '\n')

(OUT / 'findings.json').write_text(json.dumps({
    'file': str(Path(args.logo).name), 'units': U, 'size': [W_, H_], 'colours': logo.colours,
    'checks': [{k_: v for k_, v in c.items() if k_ != 'details'} for c in checks]}, indent=2, default=float) + '\n')

print(f'{NAME}: ' + ', '.join(f'{c["title"]} {c["status"]}' for c in checks))
print(f'{len(fixes)} to fix, {len(consider)} to consider. Wrote {OUT}/report.md, fix-brief.md, findings.json and '
      f'{len(list(OUT.glob("*.png")))} images in {time.time() - t0:.0f}s')

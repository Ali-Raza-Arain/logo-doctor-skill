# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Geometry measurements of a logo, the way a mark designer checks construction by eye, but with numbers.

Everything works on the analysis bitmap from common.load_logo and reports in the logo's own units.
  strokes()   stroke weights from inscribed circles along the centre line of every stroke
  gaps()      widths of the spaces between facing edges, from circles that fit in each gap
  outline()   the outline split into exact straight runs and circular arcs, plus true corners
  circles()   rings, dots and round holes; arcs that share (or nearly share) a centre; the radius system
  angles()    the angle system of straight edges and edges that sit just off it
  grid()      the construction grid that explains the key positions, and what falls off it
  alignment() positions that almost line up but miss
  symmetry(), balance(), complexity()
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.measure import find_contours
from skimage.morphology import skeletonize

K8 = np.ones((3, 3), np.uint8)


# ---------------------------------------------------------------- centre lines and inscribed circles

def _ridge(sk, dt, min_len):
    """Skeleton points that measure a stroke (or gap) cleanly: away from junctions and from loose ends, where the
    inscribed circle is distorted. Returns segments of connected points."""
    nb = (ndimage.convolve(sk.astype(np.uint8), K8, mode='constant') - 1) * sk
    junction, ends = sk & (nb >= 3), sk & (nb == 1)
    far = lambda m: ndimage.distance_transform_edt(~m) if m.any() else np.full(sk.shape, 1e9)
    # A cut or rounded end narrows the largest circle that fits for about one stroke width, so stay clear of it.
    keep = sk & (far(junction) > 2.4 * dt + 2) & (far(ends) > 3.2 * dt + 2)
    lab, _ = ndimage.label(keep, structure=K8)
    segs = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        rr, cc = np.nonzero(lab[sl] == i)
        rr, cc = rr + sl[0].start, cc + sl[1].start
        if len(rr) >= min_len:
            segs.append({'rows': rr, 'cols': cc, 'd': dt[rr, cc]})
    return segs


def edge_points(alpha, step=0.5):
    """The outline at sub-pixel precision (level 0.5 of the antialiased coverage), as points every `step` pixels."""
    pts = []
    for c in find_contours(np.pad(alpha, 1), 0.5):
        c = c - 1
        s = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
        if s[-1] < 2:
            continue
        t = np.arange(0, s[-1], step)
        pts.append(np.c_[np.interp(t, s, c[:, 0]), np.interp(t, s, c[:, 1])])
    return np.vstack(pts) if pts else np.zeros((0, 2))


def two_sided(tree, P, rows, cols):
    """Width at each centre-line point: distance to the nearest edge plus distance to the nearest edge on the other
    side. Exact even when the skeleton pixel is off the true centre. Also returns the angle (0 to 180, y up) of the
    stroke or gap at that point."""
    p = np.c_[rows, cols].astype(float)
    d1, i1 = tree.query(p)
    q1 = P[i1]
    width = np.empty(len(p))
    for n, b in enumerate(tree.query_ball_point(p, 1.6 * d1 + 3.0)):
        v = P[b] - p[n]
        far = v @ (q1[n] - p[n]) < 0
        width[n] = d1[n] + (np.sqrt((v[far] ** 2).sum(1)).min() if far.any() else d1[n])
    nrm = (p - q1) / np.maximum(d1, 1e-9)[:, None]
    ang = (np.degrees(np.arctan2(-nrm[:, 0], nrm[:, 1])) + 90) % 180
    return width, ang


def _direction(seg):
    """Straight or curved, and the angle (0 to 180, y up) of a straight segment."""
    p = np.c_[seg['cols'], -seg['rows']].astype(float)
    if len(p) < 6:
        return 'curve', None
    q = p - p.mean(0)
    _, s, vt = np.linalg.svd(q, full_matrices=False)
    off = np.abs(q @ vt[1])
    if off.max() < max(1.5, 0.02 * len(p)):
        ang = float(np.degrees(np.arctan2(vt[0][1], vt[0][0])) % 180)
        if min(ang, 180 - ang) < 15:
            return 'horizontal', ang
        if abs(ang - 90) < 15:
            return 'vertical', ang
        return 'diagonal', ang
    return 'curve', None


def _tiers(values, weights, rel=0.04):
    """Group values that run into each other (each within `rel` of the previous one when sorted)."""
    order = np.argsort(values)
    groups = []
    for i in order:
        if groups and values[i] <= values[groups[-1][-1]] * (1 + rel):
            groups[-1].append(i)
        else:
            groups.append([i])
    out = []
    for g in groups:
        v, w = np.asarray(values)[g], np.asarray(weights)[g]
        o = np.argsort(v)
        cw = np.cumsum(w[o])
        out.append({'value': float(v[o][np.searchsorted(cw, cw[-1] / 2)]), 'members': g, 'weight': float(w.sum())})
    total = sum(t['weight'] for t in out) or 1
    for t in out:
        t['share'] = t['weight'] / total
    return out


def strokes(logo):
    """Stroke weights. Each segment's width is twice the median radius of the circles that fit inside it."""
    k = logo.k
    segs = []
    for colour, a in logo.layers:
        m = a > 0.5
        if not m.any():
            continue
        dt = ndimage.distance_transform_edt(m)
        P = edge_points(a)
        tree = cKDTree(P)
        for s in _ridge(skeletonize(m), dt, min_len=max(6, int(0.01 * logo.size_px))):
            wpx, ang = two_sided(tree, P, s['rows'], s['cols'])
            w = wpx / k
            if np.median(wpx) < 3:
                continue
            cx, cy = logo.units(s['cols'].mean(), s['rows'].mean())
            segs.append({**s, 'w': w, 'ang': ang, 'colour': colour, 'width': float(np.median(w)),
                         'length': len(w) / k, 'at': (round(cx, 1), round(cy, 1)),
                         'p10': float(np.percentile(w, 10)), 'p90': float(np.percentile(w, 90))})
    if not segs:
        return {'segments': [], 'tiers': [], 'main': None, 'close_tiers': [], 'by_kind': {}, 'uneven': []}
    tiers = _tiers([s['width'] for s in segs], [s['length'] for s in segs])
    for ti, t in enumerate(tiers):
        for i in t['members']:
            segs[i]['tier'] = ti
            segs[i]['dev'] = (segs[i]['width'] - t['value']) / t['value']
    main = max(tiers, key=lambda t: t['weight'])['value']
    close = []
    real = [t for t in tiers if t['share'] > 0.02]
    for a, b in zip(real, real[1:]):
        if b['value'] / a['value'] < 1.15:
            close.append((a['value'], b['value'], a['share'], b['share']))
    # horizontal against vertical parts of the same weight tier: optically, horizontals look heavier
    by_kind = {}
    main_t = max(range(len(tiers)), key=lambda i: tiers[i]['weight'])
    w_all = np.concatenate([s['w'] for s in segs if s['tier'] == main_t])
    a_all = np.concatenate([s['ang'] for s in segs if s['tier'] == main_t])
    for kind, sel in (('horizontal', np.minimum(a_all, 180 - a_all) < 12), ('vertical', np.abs(a_all - 90) < 12),
                      ('diagonal', (np.abs(a_all - 45) < 12) | (np.abs(a_all - 135) < 12))):
        if sel.sum() > 0.03 * len(a_all):
            by_kind[kind] = {'width': float(np.median(w_all[sel])), 'share': float(sel.mean())}
    uneven = [s for s in segs if (s['p90'] - s['p10']) / s['width'] > 0.1 and s['length'] > 4 * s['width']]
    return {'segments': segs, 'tiers': tiers, 'main': main, 'close_tiers': close, 'by_kind': by_kind,
            'uneven': uneven}


def gaps(logo, main_width):
    """Widths of the narrow spaces between facing edges (counters and the margin around the logo are left out)."""
    k, m = logo.k, logo.mask
    bg = ~m
    bdt, (iy, ix) = ndimage.distance_transform_edt(bg, return_indices=True)
    H, W = m.shape
    yy, xx = np.indices(m.shape)
    to_edge = np.minimum.reduce([yy, xx, H - 1 - yy, W - 1 - xx])
    limit = max(3 * (main_width or 0) * k, 0.08 * logo.size_px) / 2
    sk = skeletonize(bg) & (bdt < to_edge - 2) & (bdt <= limit)
    py, px = np.nonzero(sk)
    facing = np.zeros(len(py), bool)
    for f in (1.15, 1.3, 1.45):
        oy = np.clip(np.round(py + (py - iy[py, px]) * f).astype(int), 0, H - 1)
        ox = np.clip(np.round(px + (px - ix[py, px]) * f).astype(int), 0, W - 1)
        facing |= m[oy, ox]
    gsk = np.zeros_like(m)
    gsk[py[facing], px[facing]] = True
    chans = []
    P = edge_points(logo.alpha)
    tree = cKDTree(P)
    for s in _ridge(gsk, bdt, min_len=max(6, int(0.01 * logo.size_px))):
        w = two_sided(tree, P, s['rows'], s['cols'])[0] / k
        cy, cx = logo.units(s['cols'].mean(), s['rows'].mean())[::-1]
        i_min = int(np.argmin(w))
        chans.append({**s, 'w': w, 'median': float(np.median(w)), 'p5': float(np.percentile(w, 5)),
                      'p95': float(np.percentile(w, 95)), 'min': float(w.min()), 'length': len(w) / k,
                      'at': (round(cx, 1), round(cy, 1)),
                      'min_at': tuple(round(v, 1) for v in logo.units(s['cols'][i_min], s['rows'][i_min]))})
    if not chans:
        return {'channels': [], 'usual': None, 'tight': [], 'uneven': []}
    med = np.array([c['median'] for c in chans])
    ln = np.array([c['length'] for c in chans])
    o = np.argsort(med)
    usual = float(med[o][np.searchsorted(np.cumsum(ln[o]), ln.sum() / 2)])
    floor = max(0.7 * usual, 0.6 * main_width) if main_width else 0.7 * usual
    tight = sorted((c for c in chans if c['p5'] < floor), key=lambda c: c['min'])
    uneven = [c for c in chans if (c['p95'] - c['p5']) / c['median'] > 0.15 and c['length'] > 3 * c['median']]
    return {'channels': chans, 'usual': usual, 'floor': floor, 'tight': tight, 'uneven': uneven,
            'narrowest': float(min(c['min'] for c in chans))}


# ---------------------------------------------------------------- the outline as lines and arcs

def _fit_line(p):
    c = p.mean(0)
    _, _, vt = np.linalg.svd(p - c, full_matrices=False)
    return c, vt[0], float(np.abs((p - c) @ vt[1]).max())


def _fit_circle(p):
    A = np.c_[2 * p, np.ones(len(p))]
    b = (p ** 2).sum(1)
    (cy, cx, c), *_ = np.linalg.lstsq(A, b, rcond=None)
    r = float(np.sqrt(max(c + cy * cy + cx * cx, 1e-9)))
    return np.array([cy, cx]), r, float(np.abs(np.hypot(p[:, 0] - cy, p[:, 1] - cx) - r).max())


def _bows(q, tol):
    """True when a short run is better described by a circle than a line: the start or end of a curve."""
    _, r, res_c = _fit_circle(q)
    res_l = _fit_line(q)[2]
    return res_l > 0.12 and res_c < 0.6 * res_l


def _longest(ok, i, n, start=8):
    """Largest j such that ok(i, j) holds, assuming it holds for every shorter run."""
    if i + start > n or not ok(i, i + start):
        return i
    lo, step = i + start, start
    while lo + step <= n and ok(i, lo + step):
        lo += step
        step *= 2
    hi = min(n, lo + step)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(i, mid):
            lo = mid
        else:
            hi = mid
    return lo


def outline(logo, tol=None):
    """Split every outline into exact straight runs and circular arcs (in analysis pixels, then units).
    A raster's edges are less exact than a rendered SVG's, so the fit tolerance follows its pixel size."""
    k, size_px = logo.k, logo.size_px
    tol = tol or (0.5 if logo.kind == 'svg' else max(0.5, 0.35 * k))
    rmax = 0.75 * size_px
    lines, arcs, corners = [], [], []
    for ci, c in enumerate(find_contours(np.pad(logo.alpha, 1), 0.5)):
        c = c - 1
        if len(c) < 24 or not np.allclose(c[0], c[-1]):
            continue
        seg = np.hypot(*np.diff(c, axis=0).T)
        s = np.r_[0, np.cumsum(seg)]
        n = int(s[-1])
        if n < 24:
            continue
        t = np.linspace(0, s[-1], n, endpoint=False)
        p = np.c_[np.interp(t, s, c[:, 0]), np.interp(t, s, c[:, 1])]
        # start at the sharpest turn, so no run is split by the start of the loop
        w = 4
        d1, d2 = np.roll(p, -w, 0) - p, p - np.roll(p, w, 0)
        turn = np.abs(np.arctan2(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0], (d1 * d2).sum(1)))
        p = np.roll(p, -int(np.argmax(turn)), 0)
        ok_line = lambda i, j: _fit_line(p[i:j])[2] < tol
        ok_arc = lambda i, j: (lambda f: f[2] < tol and 2.5 < f[1] < rmax)(_fit_circle(p[i:j]))
        items, i = [], 0
        while i < n:
            jl = _longest(ok_line, i, n)
            ja = _longest(ok_arc, i, n)
            ll, la = jl - i, ja - i
            if ll >= max(10, 0.8 * la) and not (ll < 0.06 * size_px and la >= 6 and _bows(p[i:jl], tol)):
                items.append(('line', i, jl))
                i = jl
            elif la >= 10:
                items.append(('arc', i, ja))
                i = ja
            else:
                i += 1
        for kind, i, j in items:
            q = p[i:j]
            if kind == 'line':
                m = max(1, int(0.15 * len(q)))
                cen, d, res = _fit_line(q[m:-m] if len(q) > 3 * m + 2 else q)
                ang = float(np.degrees(np.arctan2(-d[0], d[1])) % 180)
                proj = (q - cen) @ d
                a_, b_ = cen + proj.min() * d, cen + proj.max() * d
                lines.append({'contour': ci, 'i': i, 'j': j, 'angle': ang, 'length': (j - i) / k,
                              'length_px': j - i, 'centre_px': cen, 'dir': d,
                              'a': logo.units(a_[1], a_[0]), 'b': logo.units(b_[1], b_[0]),
                              'mid': logo.units(cen[1], cen[0])})
            else:
                m = max(1, int(0.08 * len(q)))
                cen, r, res = _fit_circle(q[m:-m] if len(q) > 3 * m + 8 else q)
                span = float(np.degrees((j - i) / r))
                mid = q[len(q) // 2]
                v = (cen - mid) / max(np.linalg.norm(cen - mid), 1e-9)
                probe = np.clip(np.round(mid + 2.5 * v).astype(int), 0, np.array(logo.alpha.shape) - 1)
                side = 'outer' if logo.alpha[probe[0], probe[1]] > 0.5 else 'inner'
                cx, cy = logo.units(cen[1], cen[0])
                arcs.append({'contour': ci, 'i': i, 'j': j, 'cx': cx, 'cy': cy, 'r': r / k, 'r_px': r,
                             'span': min(span, 360.0), 'side': side, 'pts': q})
        # true corners: two straight runs meeting at an angle, with at most a short rounding between them
        ln = [it for it in items if it[0] == 'line']
        base = len(lines) - len(ln)
        for a_i in range(len(ln)):
            b_i = (a_i + 1) % len(ln)
            if b_i == a_i:
                continue
            A, B = lines[base + a_i], lines[base + b_i]
            if min(A['length_px'], B['length_px']) < max(20, 0.02 * size_px):
                continue
            gap = (B['i'] - A['j']) % n
            if gap > max(6, 0.012 * size_px):
                continue
            diff = abs(A['angle'] - B['angle']) % 180
            if min(diff, 180 - diff) < 20:
                continue                                # two chords of one curve, not a corner
            M = np.array([A['dir'], -B['dir']]).T
            try:
                t1, _ = np.linalg.solve(M, B['centre_px'] - A['centre_px'])
            except np.linalg.LinAlgError:
                continue
            P = A['centre_px'] + t1 * A['dir']
            if np.min(np.hypot(*(p[[A['j'] % n, B['i'] % n]] - P).T)) > max(6, 0.012 * size_px):
                continue                                # the lines meet far from the outline: not a corner
            corners.append({'at': logo.units(P[1], P[0]), 'px': P, 'angle': min(diff, 180 - diff)})
    return {'lines': lines, 'arcs': arcs, 'corners': corners}


# ---------------------------------------------------------------- circles, centres and radii

def _clusters(points, thr):
    n = len(points)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            if np.hypot(*(np.array(points[i]) - points[j])) <= thr:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def circles(logo, arcs):
    k, size = logo.k, logo.size
    exact_tol = max(1.5 / k, 0.0015 * size)
    good = [a for a in arcs if a['span'] >= 20 and a['j'] - a['i'] >= 0.015 * logo.size_px]
    centres = [(a['cx'], a['cy']) for a in good]
    exact = []
    for g in _clusters(centres, exact_tol):
        mem = [good[i] for i in g]
        w = np.array([m['span'] for m in mem])
        cx = float(np.average([m['cx'] for m in mem], weights=w))
        cy = float(np.average([m['cy'] for m in mem], weights=w))
        exact.append({'cx': cx, 'cy': cy, 'arcs': mem})
    rings, dots, holes = [], [], []
    def by_radius(arcs_):
        """Arcs around one centre grouped by radius: [(radius, total span)]."""
        out = []
        for a in sorted(arcs_, key=lambda a: a['r']):
            if out and a['r'] - out[-1][0] <= max(0.5, 0.01 * a['r']):
                r0, sp = out[-1]
                out[-1] = ((r0 * sp + a['r'] * a['span']) / (sp + a['span']), sp + a['span'])
            else:
                out.append((a['r'], a['span']))
        return out
    for e in exact:
        inner = by_radius([a for a in e['arcs'] if a['side'] == 'inner'])
        outer = by_radius([a for a in e['arcs'] if a['side'] == 'outer'])
        full_in = [r for r, sp in inner if sp >= 300]
        full_out = [r for r, sp in outer if sp >= 300]
        e['ring'] = False
        if full_in:
            r_in = full_in[0]
            outs = [(r, sp) for r, sp in outer if r > r_in * 1.05 and sp >= 60]
            if outs and not [r for r, _ in inner if r_in < r < outs[0][0]]:
                rings.append({'cx': e['cx'], 'cy': e['cy'], 'r_in': r_in, 'r_out': outs[0][0]})
                e['ring'] = True
            elif not outs:
                holes.append({'cx': e['cx'], 'cy': e['cy'], 'r': r_in})
        elif full_out and not inner:
            dots.append({'cx': e['cx'], 'cy': e['cy'], 'r': full_out[0]})
    # rings meant to match: same look, slightly different sizes
    mismatched = []
    for g in _clusters([(r['r_in'], r['r_out']) for r in rings], 0.12 * max([r['r_out'] for r in rings] or [1])):
        if len(g) < 2:
            continue
        rs = [rings[i] for i in g]
        spread_in = max(r['r_in'] for r in rs) - min(r['r_in'] for r in rs)
        spread_out = max(r['r_out'] for r in rs) - min(r['r_out'] for r in rs)
        if max(spread_in, spread_out) > max(0.5, 0.01 * max(r['r_out'] for r in rs)):
            mismatched.append(rs)
    for kind, items in (('dots', dots), ('holes', holes)):
        for g in _clusters([(d['r'], 0) for d in items], 0.08 * max([d['r'] for d in items] or [1])):
            rs = [items[i] for i in g]
            if len(rs) > 1 and max(d['r'] for d in rs) - min(d['r'] for d in rs) > max(0.5, 0.01 * rs[0]['r']):
                mismatched.append(rs)
    # arcs around nearly the same centre: usually meant to be concentric
    near = []
    big = [e for e in exact if sum(a['span'] for a in e['arcs']) >= 90]
    for g in _clusters([(e['cx'], e['cy']) for e in big], 0.015 * size):
        if len(g) < 2:
            continue
        es = sorted((big[i] for i in g), key=lambda e: -sum(a['span'] for a in e['arcs']))
        ref = es[0]
        for e in es[1:]:
            off = float(np.hypot(e['cx'] - ref['cx'], e['cy'] - ref['cy']))
            if off > exact_tol:
                near.append({'ref': ref, 'other': e, 'offset': off})
    # the radius system: radii that differ by a hair across separate centres
    radii = []
    for ei, e in enumerate(exact):
        for a in e['arcs']:
            radii.append((a['r'], ei, a))
    close_radii, seen = [], set()
    for x in range(len(radii)):
        for y in range(x + 1, len(radii)):
            (r1, e1, a1), (r2, e2, a2) = radii[x], radii[y]
            if e1 == e2 or a1['side'] != a2['side'] or (exact[e1]['ring'] and exact[e2]['ring']):
                continue
            d = abs(r1 - r2)
            if max(0.5, 0.008 * max(r1, r2)) < d < 0.05 * max(r1, r2):
                key = (round(min(r1, r2), 1), round(max(r1, r2), 1))
                if key not in seen:
                    seen.add(key)
                    close_radii.append({'r1': min(r1, r2), 'r2': max(r1, r2),
                                        'at1': (a1['cx'], a1['cy']), 'at2': (a2['cx'], a2['cy'])})
    return {'centres': exact, 'rings': rings, 'dots': dots, 'holes': holes, 'mismatched': mismatched,
            'near_concentric': near, 'close_radii': close_radii, 'exact_tol': exact_tol}


# ---------------------------------------------------------------- angles, grid, alignment

def angles(lines, size_px, snap=45.0, raster=False):
    long = [l for l in lines if l['length_px'] >= max(20, (0.05 if raster else 0.035) * size_px)]
    system, off = {}, []
    for l in long:
        near = (round(l['angle'] / snap) * snap) % 180 if snap else l['angle']
        dev = abs(l['angle'] - near)
        dev = min(dev, 180 - dev)
        tol = max(0.15, float(np.degrees(1.0 / l['length_px'])))
        l['snap'], l['dev'], l['on'] = near, dev, dev <= tol
        system[near] = system.get(near, 0) + 1
        if snap and tol < dev < 6:
            off.append(l)
    return {'lines': long, 'system': dict(sorted(system.items())), 'off': off, 'snap': snap}


def key_positions(logo, ol, circ):
    """Positions a designer would set on a grid: vertical and horizontal edges, circle centres, true corners."""
    xs, ys = [], []
    for l in ol['lines']:
        if l['length_px'] < 0.04 * logo.size_px:
            continue
        if abs(l['angle'] - 90) < 0.5:
            xs.append((l['mid'][0], 'vertical edge', l['mid']))
        elif min(l['angle'], 180 - l['angle']) < 0.5:
            ys.append((l['mid'][1], 'horizontal edge', l['mid']))
    for e in circ['centres']:
        if sum(a['span'] for a in e['arcs']) >= 45:
            xs.append((e['cx'], 'arc centre', (e['cx'], e['cy'])))
            ys.append((e['cy'], 'arc centre', (e['cx'], e['cy'])))
    for c in ol['corners']:
        xs.append((c['at'][0], 'corner', c['at']))
        ys.append((c['at'][1], 'corner', c['at']))

    def dedupe(v):
        out = []
        for item in sorted(v, key=lambda t: t[0]):
            if not out or abs(item[0] - out[-1][0]) > 0.3 / max(logo.k, 1e-9) + 0.05:
                out.append(item)
        return out
    return dedupe(xs), dedupe(ys)


NICE = [1, 1.25, 2, 2.5, 4, 5, 8, 10]


def grid(logo, xs, ys, module=None, origin=(0.0, 0.0)):
    size = logo.size
    tol = max(1.0 / logo.k, 0.0015 * size)
    pos = [(v, 'x', what, at) for v, what, at in xs] + [(v, 'y', what, at) for v, what, at in ys]
    if len(pos) < 8 and not module:
        return {'module': None, 'coverage': 0, 'off': [], 'tol': tol, 'origin': origin, 'positions': pos,
                'too_few': True}

    def coverage(u, org):
        hit = []
        for v, axis, what, at in pos:
            o = org[0] if axis == 'x' else org[1]
            r = (v - o) / u
            hit.append(abs(r - round(r)) * u <= tol)
        return float(np.mean(hit)), hit
    if module:
        cov, hit = coverage(module, origin)
        best = (module, cov, hit)
    else:
        # A position falls near some line of a fine grid by chance; score each module by how far it beats chance,
        # then take the largest module that scores close to the best.
        # Round numbers from the file's origin (how most designers set up a grid), and fractions of the mark's
        # height or width from its top left corner (a grid drawn around the mark, or a raster at any scale).
        cands = [(n * 10 ** e, origin, None) for e in range(-2, 5) for n in NICE
                 if size / 150 <= n * 10 ** e <= size / 6]
        bx0, by0, bx1, by1 = logo.bbox
        for side in (by1 - by0, bx1 - bx0):
            for cells in range(6, 151):
                if size / 150 <= side / cells <= size / 6:
                    cands.append((side / cells, (bx0, by0), cells))
        scored = []
        for u, org, cells in cands:
            chance = min(1.0, 2 * tol / u)
            if chance >= 0.5:
                continue
            cov, hit = coverage(u, org)
            scored.append(((cov - chance) / (1 - chance), u, cov, hit, org, cells is None))
        if not scored or max(t[0] for t in scored) < 0.5:
            return {'module': None, 'coverage': 0.0, 'off': [], 'tol': tol, 'origin': origin, 'positions': pos}
        top = max(t[0] for t in scored)
        near_top = [t for t in scored if t[0] >= top - 0.03]
        widest = max(t[1] for t in near_top)
        nice = [t for t in near_top if t[5] and t[1] >= 0.75 * widest]
        _, u, cov, hit, origin, _ = max(nice or near_top, key=lambda t: t[1])
        best = (u, cov, hit)
    u, cov, hit = best
    off = []
    for (v, axis, what, at), h in zip(pos, hit):
        if not h:
            o = origin[0] if axis == 'x' else origin[1]
            g = o + round((v - o) / u) * u
            off.append({'axis': axis, 'value': v, 'grid': g, 'offset': v - g, 'what': what, 'at': at})
    return {'module': u, 'coverage': cov, 'off': off, 'tol': tol, 'origin': origin, 'positions': pos,
            'cells': ((logo.bbox[2] - logo.bbox[0]) / u, (logo.bbox[3] - logo.bbox[1]) / u)}


def alignment(logo, xs, ys, grid_result=None):
    """Edges and centres that almost share a row or column. Corners are left out (they follow from edges), and
    positions that run into each other are reported once, as one group."""
    tol = max(1.0 / logo.k, 0.0015 * logo.size)
    hi = 0.012 * logo.size
    off_grid = {(o['axis'], round(o['value'], 2)) for o in (grid_result or {}).get('off', [])}
    gridded = bool(grid_result and grid_result.get('module'))
    misses = []
    for axis, vals in (('x', xs), ('y', ys)):
        vals = sorted((v for v in vals if v[1] != 'corner'), key=lambda v: v[0])
        group = []
        for v in vals + [None]:
            if v is not None and group and v[0] - group[-1][0] < hi:
                group.append(v)
                continue
            if len(group) > 1 and group[-1][0] - group[0][0] > tol:
                if not gridded or any((axis, round(g[0], 2)) in off_grid for g in group):
                    misses.append({'axis': axis, 'a': group[0], 'b': group[-1], 'members': group,
                                   'diff': group[-1][0] - group[0][0]})
            group = [v] if v is not None else []
    return {'misses': misses, 'tol': tol}


# ---------------------------------------------------------------- symmetry, balance, complexity

def symmetry(logo):
    x0, y0, x1, y1 = logo.bbox_px
    crop = logo.mask[y0:y1, x0:x1]
    f = max(1, int(max(crop.shape) / 500))
    small = ndimage.zoom(crop.astype(np.float32), 1 / f, order=1) > 0.5
    variants = {'mirror left to right': lambda a: a[:, ::-1], 'mirror top to bottom': lambda a: a[::-1, :],
                'turn by 180 degrees': lambda a: a[::-1, ::-1]}
    def shifted(a, dy, dx):
        """a moved by (dy, dx) pixels, filled with empty space."""
        out = np.zeros_like(a)
        H, W = a.shape
        out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = \
            a[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
        return out

    def best_shift(a, ref, R, centre=(0, 0)):
        best = (-1, 0, 0)
        for dy in range(centre[0] - R, centre[0] + R + 1):
            for dx in range(centre[1] - R, centre[1] + R + 1):
                sh = shifted(ref, dy, dx)
                iou = np.logical_and(a, sh).sum() / max(np.logical_or(a, sh).sum(), 1)
                if iou > best[0]:
                    best = (iou, dy, dx)
        return best
    out = {}
    tiny = ndimage.zoom(small.astype(np.float32), 0.5, order=1) > 0.5
    for name, fn in variants.items():
        # The copy is moved to fit the mark best, so a mark that is symmetric apart from one part
        # still lines up, and only that part shows as a difference. Coarse search, then fine.
        _, cy, cx_ = best_shift(tiny, fn(tiny), max(4, int(0.05 * max(tiny.shape))))
        _, dy, dx = best_shift(small, fn(small), 2, (2 * cy, 2 * cx_))
        ref = shifted(fn(crop), dy * f, dx * f)
        inter, union = np.logical_and(crop, ref).sum(), np.logical_or(crop, ref).sum()
        here, there = crop & ~ref, ref & ~crop
        d_ref = ndimage.distance_transform_edt(~ref)
        d_sh = ndimage.distance_transform_edt(~crop)
        dev = np.r_[d_ref[here], d_sh[there]] / logo.k
        near = (d_ref[crop] <= 0.03 * logo.size_px).mean()
        max_dev = float(dev.max()) if len(dev) else 0.0
        if max_dev <= max(1.5 / logo.k, 0.0025 * logo.size):
            verdict = 'symmetric'
        elif near >= 0.97 and max_dev <= 0.06 * logo.size:
            verdict = 'nearly'
        else:
            verdict = 'no'
        out[name] = {'iou': float(inter / max(union, 1)), 'shift_px': (dy * f, dx * f), 'only_here': here,
                     'only_there': there, 'origin': (x0, y0), 'max_dev': max_dev, 'near': float(near),
                     'verdict': verdict}
    rank = {'symmetric': 2, 'nearly': 1, 'no': 0}
    best = max(out, key=lambda n: (rank[out[n]['verdict']], out[n]['iou']))
    return {'variants': out, 'best': best}


def balance(logo):
    m = logo.mask
    ys, xs = np.nonzero(m)
    cx, cy = logo.units(xs.mean(), ys.mean())
    bx0, by0, bx1, by1 = logo.bbox
    mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
    w, h = bx1 - bx0, by1 - by0
    px0, py0 = logo.px(mx, my)
    q = {'top left': ((ys < py0) & (xs < px0)).mean(), 'top right': ((ys < py0) & (xs >= px0)).mean(),
         'bottom left': ((ys >= py0) & (xs < px0)).mean(), 'bottom right': ((ys >= py0) & (xs >= px0)).mean()}
    return {'centroid': (cx, cy), 'centre': (mx, my), 'dx': (cx - mx) / w, 'dy': (my - cy) / h,
            'quadrants': {k_: float(v) for k_, v in q.items()}, 'top': float((ys < py0).mean()),
            'left': float((xs < px0).mean()), 'ink_share': float(m[logo.bbox_px[1]:logo.bbox_px[3],
                                                                    logo.bbox_px[0]:logo.bbox_px[2]].mean())}


def complexity(logo, ol, circ):
    m = logo.mask
    _, parts = ndimage.label(m, structure=K8)
    bl, nb = ndimage.label(~m)
    edge = set(np.unique(np.r_[bl[0], bl[-1], bl[:, 0], bl[:, -1]]))
    holes = sum(1 for i in range(1, nb + 1) if i not in edge)
    perim = sum(l['length'] for l in ol['lines']) + sum(np.radians(a['span']) * a['r'] for a in ol['arcs'])
    area = m.sum() / logo.k ** 2
    return {'parts': int(parts), 'holes': int(holes), 'lines': len(ol['lines']), 'arcs': len(ol['arcs']),
            'rings': len(circ['rings']), 'edge_index': float(perim / np.sqrt(max(area, 1e-9)))}

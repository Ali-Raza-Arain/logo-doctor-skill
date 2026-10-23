# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Draws the demo mark used in the guide and the tests: a letter S made of three parallel circuit traces with ring
nodes, built on a 20-unit grid in a 1000 x 1000 artboard. It belongs to no one; use it freely.

Two versions:
  fixed  everything on the grid, every trace 40 wide with 40-unit gaps, concentric bends, identical rings, exact
         45 degree cuts, and the mark is the same when turned upside down (180 degree symmetry);
  draft  the same mark with six faults of the kind generated or hurried artwork often has, so the review has
         something to find:
           1. the middle trace is 44 wide instead of 40;
           2. one bend in the lower bowl is not concentric with the others, so its gap widens from 40 to 56;
           3. the lower ring is 19 / 64 instead of 22 / 62;
           4. the cut at the end of the top trace is 42 degrees instead of 45;
           5. the upper ring sits 6 units right of the grid;
           6. a consequence of 2: the lowest trace sits 16 units below where the grid and the symmetry put it.

Usage: python make_demo.py out-folder [--colour #1d5e74]
Writes demo-draft.svg and demo-fixed.svg.
"""
import argparse
import math
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--colour', default='#1d5e74')
args = ap.parse_args()


def fmt(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.')


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def trace(segments, width, start_cap, end_cap):
    """Outline of a trace with exact arcs. segments: ('L', P, Q) or ('A', C, r, P, Q, ccw), joined tangentially.
    Caps: ('butt',) or ('cut', angle_deg, sign). Coordinates are screen coordinates (y down)."""
    d = width / 2

    def tangent(seg, at_end):
        if seg[0] == 'L':
            return unit((seg[2][0] - seg[1][0], seg[2][1] - seg[1][1]))
        C, P = seg[1], seg[4] if at_end else seg[3]
        u = unit((P[0] - C[0], P[1] - C[1]))
        return (u[1], -u[0]) if seg[5] else (-u[1], u[0])

    def offset(P, t, s):
        n = (t[1], -t[0])                                   # left of the travel direction
        return (P[0] + s * d * n[0], P[1] + s * d * n[1])

    def corners(P, t_out, cap, s_left):
        """Left and right corners at an end; t_out points out of the trace."""
        L, R = offset(P, t_out, s_left), offset(P, t_out, -s_left)
        if cap[0] == 'cut':
            c = d / math.tan(math.radians(cap[1])) * cap[2]
            L = (L[0] + c * t_out[0], L[1] + c * t_out[1])
            R = (R[0] - c * t_out[0], R[1] - c * t_out[1])
        return L, R

    first, last = segments[0], segments[-1]
    t0 = tangent(first, False)
    tn = tangent(last, True)
    sL, sR = corners(first[1] if first[0] == 'L' else first[3], (-t0[0], -t0[1]), start_cap, -1)
    eL, eR = corners(last[2] if last[0] == 'L' else last[4], tn, end_cap, 1)

    # left side forward
    cmds = [f'M{fmt(sL[0])},{fmt(sL[1])}']
    for i, seg in enumerate(segments):
        if seg[0] == 'L':
            Q = eL if i == len(segments) - 1 else offset(seg[2], tangent(seg, True), 1)
            cmds.append(f'L{fmt(Q[0])},{fmt(Q[1])}')
        else:
            C, r, P, Q, ccw = seg[1:]
            rr = r - d if ccw else r + d
            Qo = offset(Q, tangent(seg, True), 1)
            cmds.append(f'A{fmt(rr)},{fmt(rr)} 0 0 {0 if ccw else 1} {fmt(Qo[0])},{fmt(Qo[1])}')
    cmds.append(f'L{fmt(eR[0])},{fmt(eR[1])}')
    # right side backward
    for i, seg in reversed(list(enumerate(segments))):
        if seg[0] == 'L':
            P = sR if i == 0 else offset(seg[1], tangent(seg, False), -1)
            cmds.append(f'L{fmt(P[0])},{fmt(P[1])}')
        else:
            C, r, P, Q, ccw = seg[1:]
            rr = r + d if ccw else r - d
            Po = offset(P, tangent(seg, False), -1)
            cmds.append(f'A{fmt(rr)},{fmt(rr)} 0 0 {1 if ccw else 0} {fmt(Po[0])},{fmt(Po[1])}')
    return ' '.join(cmds) + ' Z'


def ring(cx, cy, r_in, r_out):
    c = lambda r: (f'M{fmt(cx - r)},{fmt(cy)} a{fmt(r)},{fmt(r)} 0 1,0 {fmt(2 * r)},0 '
                   f'a{fmt(r)},{fmt(r)} 0 1,0 {fmt(-2 * r)},0 Z')
    return c(r_out) + ' ' + c(r_in)


def mark(draft):
    """Each trace is named by its radius in the upper bowl: 240 (outermost at the top), 160 (middle), 80."""
    width = {240: 40, 160: 44 if draft else 40, 80: 40}
    top_c = (400, 340)
    bot_c = {240: (600, 660), 160: (600, 660), 80: (600, 668) if draft else (600, 660)}
    node_top = (726 if draft else 720, 180, 22, 62)
    node_bot = (280, 820, 19, 64) if draft else (280, 820, 22, 62)
    cut_top = {240: 640, 80: 480}                            # x where the cut traces end at the top
    paths = []
    for r in (240, 160, 80):
        C2 = bot_c[r]
        r2 = C2[1] - (top_c[1] + r)                          # the lower bend continues the middle bar
        y_top, y_mid, y_bot = top_c[1] - r, top_c[1] + r, C2[1] + r2
        if r == 160:
            x_start, x_end = node_top[0] - (node_top[2] + node_top[3]) / 2, node_bot[0] + (node_bot[2] + node_bot[3]) / 2
            caps = (('butt',), ('butt',))
        else:
            x_start = cut_top[r]
            x_end = 1000 - cut_top[320 - r]                  # the lower end mirrors the upper end of the other trace
            angle = 42 if (draft and r == 240) else 45
            caps = (('cut', angle, 1), ('cut', 45, -1))
        segs = [('L', (x_start, y_top), (top_c[0], y_top)),
                ('A', top_c, r, (top_c[0], y_top), (top_c[0] - r, top_c[1]), True),
                ('A', top_c, r, (top_c[0] - r, top_c[1]), (top_c[0], y_mid), True),
                ('L', (top_c[0], y_mid), (C2[0], y_mid)),
                ('A', C2, r2, (C2[0], y_mid), (C2[0] + r2, C2[1]), False),
                ('A', C2, r2, (C2[0] + r2, C2[1]), (C2[0], y_bot), False),
                ('L', (C2[0], y_bot), (x_end, y_bot))]
        paths.append(trace(segs, width[r], *caps))
    paths.append(ring(*node_top))
    paths.append(ring(*node_bot))
    body = ''.join(f'<path fill="{args.colour}" fill-rule="evenodd" d="{d}"/>' for d in paths)
    title = 'Demo mark, draft with faults' if draft else 'Demo mark'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><title>{title}</title>'
            f'{body}</svg>\n')


out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
(out / 'demo-draft.svg').write_text(mark(True))
(out / 'demo-fixed.svg').write_text(mark(False))
print(f'wrote {out / "demo-draft.svg"} and {out / "demo-fixed.svg"}')

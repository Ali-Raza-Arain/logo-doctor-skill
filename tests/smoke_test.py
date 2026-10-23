# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Smoke and regression test: builds the demo marks, reviews them, and checks the results.

The draft demo has six known faults, so the review must flag the grid, stroke weights, gaps, circles, angles and
symmetry, and the fixed demo must pass every construction check, as an SVG and as a PNG.

Usage: python tests/smoke_test.py [--keep out-folder]
Run it with the Python from setup_env.sh, or any Python with requirements.txt installed and Chromium for Playwright.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'skills' / 'logo-doctor' / 'scripts'
CONSTRUCTION = ['grid', 'alignment', 'strokes', 'gaps', 'circles', 'angles', 'symmetry']

ap = argparse.ArgumentParser()
ap.add_argument('--keep')
args = ap.parse_args()
out = Path(args.keep) if args.keep else Path(tempfile.mkdtemp(prefix='logo-doctor-test-'))
if args.keep and out.exists() and any(out.iterdir()):
    raise SystemExit(f'{out} is not empty; choose a new folder')
out.mkdir(parents=True, exist_ok=True)
failures = []


def run(name, *cmd):
    t0 = time.time()
    res = subprocess.run([sys.executable, *map(str, cmd)], capture_output=True, text=True)
    print(f'{"ok  " if res.returncode == 0 else "FAIL"} {name} ({time.time() - t0:.1f}s)')
    if res.returncode:
        failures.append(name)
        print(res.stdout[-2000:], res.stderr[-3000:], sep='\n')
    return res.returncode == 0


def status(review):
    return {c['key']: c['status'] for c in json.loads((out / review / 'findings.json').read_text())['checks']}


def expect(name, cond, detail=''):
    print(f'{"ok  " if cond else "FAIL"} {name}{": " + detail if detail and not cond else ""}')
    if not cond:
        failures.append(name)


run('demo marks', ROOT / 'examples' / 'make_demo.py', out)
if run('review draft', SCRIPTS / 'review.py', out / 'demo-draft.svg', '--out', out / 'draft'):
    s = status('draft')
    for key in ('grid', 'strokes', 'gaps', 'circles', 'angles', 'symmetry'):
        expect(f'draft: {key} is flagged', s.get(key) == 'Fix', f'got {s.get(key)}')
    for f in ('report.md', 'fix-brief.md', '01-grid.png', '02-strokes.png', '09-colour-backgrounds.png'):
        expect(f'draft: wrote {f}', (out / 'draft' / f).exists())
if run('review fixed', SCRIPTS / 'review.py', out / 'demo-fixed.svg', '--out', out / 'fixed',
       '--baseline', out / 'draft' / 'findings.json'):
    s = status('fixed')
    bad = {k: s.get(k) for k in CONSTRUCTION if s.get(k) != 'Pass'}
    expect('fixed: every construction check passes', not bad, str(bad))
    expect('fixed: report compares with the draft', '| Before |' in (out / 'fixed' / 'report.md').read_text())

sys.path.insert(0, str(SCRIPTS))
try:
    from common import Renderer
    with Renderer() as r:
        svg = (out / 'demo-fixed.svg').read_text().replace('<svg ', '<svg width="1024" height="1024" ', 1)
        r.png(svg, 1024, 1024, False, background='#ffffff').save(out / 'demo-fixed.png')
    if run('review fixed PNG', SCRIPTS / 'review.py', out / 'demo-fixed.png', '--out', out / 'fixed-png'):
        s = status('fixed-png')
        bad = {k: s.get(k) for k in CONSTRUCTION if s.get(k) != 'Pass'}
        expect('fixed PNG: every construction check passes', not bad, str(bad))
except Exception as e:                                       # noqa: BLE001
    expect('render PNG', False, repr(e))

print()
if failures:
    print(f'{len(failures)} failed: {", ".join(failures)}. Results kept in {out}')
    sys.exit(1)
print(f'all passed. Results in {out}' if args.keep else 'all passed')
if not args.keep:
    shutil.rmtree(out)

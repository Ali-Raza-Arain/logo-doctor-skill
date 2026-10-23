# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Rebuilds everything the README shows: the demo marks in examples/, their sample reviews (examples/review-draft
and examples/review-fixed, the fixed one compared with the draft), and the images in docs/images.

Usage: python tools/make_readme_images.py
Run it with the Python from setup_env.sh. It replaces only the files it generates.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'skills' / 'logo-doctor' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from common import Renderer, font  # noqa: E402

EX, IMG = ROOT / 'examples', ROOT / 'docs' / 'images'
IMG.mkdir(parents=True, exist_ok=True)


def run(*cmd):
    subprocess.run([sys.executable, *map(str, cmd)], check=True)


run(EX / 'make_demo.py', EX)
for name in ('draft', 'fixed'):
    shutil.rmtree(EX / f'review-{name}', ignore_errors=True)
run(SCRIPTS / 'review.py', EX / 'demo-draft.svg', '--out', EX / 'review-draft', '--name', 'Demo mark, draft')
run(SCRIPTS / 'review.py', EX / 'demo-fixed.svg', '--out', EX / 'review-fixed', '--name', 'Demo mark, fixed',
    '--baseline', EX / 'review-draft' / 'findings.json')


def labelled(panels, out, width=640, gap=24):
    tiles = []
    for label, img in panels:
        img = img.convert('RGB')
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
        tiles.append((label, img))
    h = max(t.height for _, t in tiles) + 56
    sheet = Image.new('RGB', (len(tiles) * (width + gap) + gap, h + gap), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(tiles):
        x = gap + i * (width + gap)
        d.text((x, 14), label, fill=(30, 30, 30), font=font(26))
        sheet.paste(img, (x, 56))
    sheet.save(IMG / out, optimize=True)


with Renderer() as r:
    marks = [(lab, r.png((EX / f'demo-{n}.svg').read_text().replace('<svg ', '<svg width="560" height="560" ', 1),
                         560, 560, False, background='#ffffff'))
             for lab, n in (('Draft: six hidden faults', 'draft'), ('Fixed: every check passes', 'fixed'))]
labelled(marks, 'hero.png', width=560)

for f, title in (('01-grid', 'grid'), ('02-strokes', 'strokes'), ('03-gaps', 'gaps'), ('04-circles', 'circles'),
                 ('05-angles', 'angles'), ('06-symmetry', 'symmetry')):
    labelled([('Draft', Image.open(EX / 'review-draft' / f'{f}.png')),
              ('Fixed', Image.open(EX / 'review-fixed' / f'{f}.png'))], f'{title}.png')
for f, title, w in (('07-balance', 'balance', 640), ('08-sizes', 'sizes', 900),
                    ('09-colour-backgrounds', 'colour-backgrounds', 1100), ('10-colour-vision', 'colour-vision', 560)):
    labelled([('', Image.open(EX / 'review-fixed' / f'{f}.png'))], f'{title}.png', width=w)
print(f'updated {EX} and {IMG}')

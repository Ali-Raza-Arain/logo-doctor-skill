# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Packs skills/logo-doctor into dist/logo-doctor.zip, the file to upload where a skill is added as a ZIP
(for example the Skills settings in the Claude apps). A copy named logo-doctor.skill is written too.

Usage: python tools/package_skill.py
"""
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / 'skills' / 'logo-doctor'
DIST = ROOT / 'dist'
SKIP = {'__pycache__', '.DS_Store'}

front = re.match(r'---\n(.*?)\n---\n', (SKILL / 'SKILL.md').read_text(), re.S)
if not front:
    raise SystemExit('SKILL.md has no frontmatter')
name = re.search(r'^name: (.+)$', front.group(1), re.M).group(1).strip()
desc = re.search(r'^description: (.+)$', front.group(1), re.M).group(1).strip()
if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name) or len(name) > 64:
    raise SystemExit(f'bad skill name {name!r}')
if len(desc) > 1024 or '<' in desc or '>' in desc:
    raise SystemExit('the description must be at most 1024 characters, without angle brackets')

DIST.mkdir(exist_ok=True)
out = DIST / f'{name}.zip'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(SKILL.rglob('*')):
        if f.is_file() and not SKIP.intersection(f.parts):
            z.write(f, Path(name) / f.relative_to(SKILL))
shutil.copy2(out, DIST / f'{name}.skill')
print(f'wrote {out} and {out.with_suffix(".skill")} ({out.stat().st_size // 1024} KB)')

# Contributing

Thank you for helping. Bug reports, better thresholds, new checks and clearer explanations are all welcome.

## Ground rules

- **Local only.** No tool may send a logo, or anything made from one, over the network. The only network use
  allowed is the one-time setup.
- **Report, never change.** The review measures and suggests; it never edits the logo. Fixes happen in separate
  steps the user chooses.
- **Never overwrite.** Tools write to new or empty folders, or refuse and explain, unless `--force` is passed.
- **Only shareable images.** Use the demo marks or images you have the right to share in issues, tests and docs.
  Never attach a client's or employer's logo.
- **Honest thresholds.** Every threshold is documented in `references/measurements.md`, with its known false
  positives. A new check needs both.

## Development setup

```bash
bash skills/logo-doctor/scripts/setup_env.sh
PY=~/.cache/logo-doctor/venv/bin/python
$PY tests/smoke_test.py
```

## Before opening a pull request

1. Run `python tests/smoke_test.py`. The draft demo must still flag all its faults, and the fixed demo must pass
   every construction check, as SVG and PNG.
2. Look at the images, not only the test result: run `python tools/make_readme_images.py` and open
   `examples/review-draft` and `examples/review-fixed`. A check that passes but draws misleading circles is a bug.
3. Try a real logo you are free to use, ideally a traced or hand-drawn one, and make sure the report stays short
   and useful (findings grouped, not repeated).
4. Update `docs/cli.md`, `CHANGELOG.md`, `references/measurements.md` and, if the workflow changes, `SKILL.md`.
   Keep the skill description under 1024 characters; `python tools/package_skill.py` checks it.
5. If you add a dependency, add it to `requirements.txt`, `skills/logo-doctor/scripts/setup_env.sh` and
   `THIRD_PARTY_NOTICES.md`.

## Style

- Python 3.10 or newer, standard library plus the listed dependencies.
- Measurements live in `measure.py` and `colours.py` and return plain data; drawing and wording live in `review.py`.
- Report text is plain, concrete English in sentence case, with numbers and the image to look at.

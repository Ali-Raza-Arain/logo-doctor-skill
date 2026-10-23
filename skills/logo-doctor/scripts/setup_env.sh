#!/usr/bin/env bash
# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
# One-time setup for the logo-doctor scripts, in a private virtual environment (nothing is installed system-wide):
# Pillow, NumPy, SciPy, scikit-image, Playwright and its Chromium build.
#
# Location: $LOGO_DOCTOR_HOME, default ~/.cache/logo-doctor. Afterwards run the scripts with
#   ~/.cache/logo-doctor/venv/bin/python scripts/review.py ...
# Everything runs locally. The only downloads are the packages and the Chromium build.
set -euo pipefail

HOME_DIR="${LOGO_DOCTOR_HOME:-$HOME/.cache/logo-doctor}"
VENV="$HOME_DIR/venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  python3 -m venv "$VENV"
fi
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet pillow numpy scipy scikit-image playwright

# Chromium renders SVGs exactly as browsers do. A system Chrome is used as a fallback if this download fails.
"$PY" -m playwright install chromium || echo "Chromium download failed; the scripts will try a system Chrome instead."

"$PY" - <<'PYEOF'
import importlib
for m in ('PIL', 'numpy', 'scipy', 'skimage', 'playwright'):
    importlib.import_module(m)
print('logo-doctor environment ready')
PYEOF
echo "Python: $PY"

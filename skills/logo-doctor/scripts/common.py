# logo-doctor, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-doctor-skill
"""Shared helpers for logo-doctor: loading a logo (SVG or raster) into an analysis bitmap with a known mapping back to
the logo's own units, rendering with headless Chromium, colour maths and drawing annotated images.

Units: for an SVG, the SVG's own user units (what a designer sees in the file and in a design tool); for a raster,
the source image's pixels. Every measurement in a report is in these units.
"""
from __future__ import annotations

import re
import shutil
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
SKILL_DIR = Path(__file__).resolve().parent.parent
FONT = SKILL_DIR / 'assets' / 'fonts' / 'InstrumentSans-Variable-latin.ttf'


# ---------------------------------------------------------------- colour

def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(round(min(255, max(0, c)))) for c in rgb)


def to_linear(c):
    c = np.asarray(c, np.float64) / 255
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def from_linear(c):
    c = np.clip(np.asarray(c, np.float64), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def luminance(h):
    r, g, b = to_linear(hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def oklab(h):
    """sRGB hex to OKLab (Bjorn Ottosson, 2020)."""
    r, g, b = to_linear(hex_to_rgb(h))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = np.cbrt([l, m, s])
    return np.array([0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                     1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                     0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s])


def oklab_to_hex(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s]
    return rgb_to_hex(from_linear(rgb)), all(-1e-4 <= v <= 1 + 1e-4 for v in rgb)


def oklch(h):
    L, a, b = oklab(h)
    return L, float(np.hypot(a, b)), float(np.degrees(np.arctan2(b, a)) % 360)


def from_oklch(L, C, H):
    """OKLCH to hex, reducing chroma until the colour fits in sRGB."""
    for _ in range(60):
        hx, ok = oklab_to_hex((L, C * np.cos(np.radians(H)), C * np.sin(np.radians(H))))
        if ok:
            return hx
        C *= 0.95
    return hx


def delta_ok(a, b):
    """Distance in OKLab. About 0.02 is a just noticeable difference; under 0.1 colours read as close."""
    return float(np.linalg.norm(oklab(a) - oklab(b)))


# Colour vision deficiency simulation, Machado, Oliveira and Fernandes (2009), severity 1.0, in linear RGB.
CVD = {
    'protanopia': np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
    'deuteranopia': np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    'tritanopia': np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602],
                            [0.004733, 0.691367, 0.303900]]),
}


def simulate(h, kind):
    if kind == 'greyscale':
        v = from_linear([luminance(h)] * 3)
        return rgb_to_hex(v)
    return rgb_to_hex(from_linear(CVD[kind] @ to_linear(hex_to_rgb(h))))


def simulate_image(img, kind):
    a = np.asarray(img.convert('RGB')).astype(np.float64)
    lin = to_linear(a)
    if kind == 'greyscale':
        y = lin @ np.array([0.2126, 0.7152, 0.0722])
        out = np.repeat(y[..., None], 3, -1)
    else:
        out = lin @ CVD[kind].T
    return Image.fromarray(np.clip(from_linear(out) + 0.5, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- rendering

def _chrome():
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        p = shutil.which(name)
        if p:
            return p
    return None


class Renderer:
    """Headless Chromium, so SVGs are drawn exactly as browsers draw them."""

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        try:
            self._browser = self._pw.chromium.launch()
        except Exception:
            exe = _chrome()
            if not exe:
                raise SystemExit('No Chromium found. Run scripts/setup_env.sh, or install Google Chrome.')
            self._browser = self._pw.chromium.launch(executable_path=exe)
        self.page = self._browser.new_page()
        return self

    def __exit__(self, *exc):
        self._browser.close()
        self._pw.stop()

    def png(self, svg_text, w, h, transparent=True, background='transparent'):
        w, h = int(round(w)), int(round(h))
        self.page.set_viewport_size({'width': w, 'height': h})
        self.page.set_content(f'<html><body style="margin:0;background:{background}">{svg_text}</body></html>')
        self.page.wait_for_timeout(50)
        shot = self.page.screenshot(omit_background=transparent, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        return Image.open(BytesIO(shot)).convert('RGBA' if transparent else 'RGB')


_ROOT = re.compile(r'<svg\b[^>]*>', re.S)


def svg_viewbox(text):
    root = _ROOT.search(text)
    if not root:
        raise SystemExit('not an SVG file')
    vb = re.search(r'viewBox\s*=\s*"([^"]+)"', root.group(0))
    if vb:
        return [float(v) for v in vb.group(1).replace(',', ' ').split()]
    w = re.search(r'\swidth\s*=\s*"([\d.]+)', root.group(0))
    h = re.search(r'\sheight\s*=\s*"([\d.]+)', root.group(0))
    if w and h:
        return [0.0, 0.0, float(w.group(1)), float(h.group(1))]
    raise SystemExit('the SVG has neither a viewBox nor a width and height')


def svg_region(text, x, y, w, h, wpx, hpx):
    """The same SVG showing the region (x, y, w, h) of its own coordinates at wpx by hpx pixels."""
    root = _ROOT.search(text).group(0)
    new = re.sub(r'\s(width|height|viewBox|preserveAspectRatio|x|y)\s*=\s*"[^"]*"', '', root)
    new = new[:-1].rstrip('/') + (f' width="{wpx}" height="{hpx}" viewBox="{x} {y} {w} {h}" '
                                  'preserveAspectRatio="none">')
    return text.replace(root, new, 1)


NAMED = {'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'green': '#008000', 'blue': '#0000ff'}


def svg_colours(text):
    """Solid fill and stroke colours named in the SVG (attributes and inline styles)."""
    found = []
    for m in re.finditer(r'(?:fill|stroke|stop-color)\s*[:=]\s*"?\s*(#[0-9a-fA-F]{3,6}\b|rgb\([^)]*\)|[a-zA-Z]+)', text):
        v = m.group(1).lower()
        if v.startswith('rgb('):
            v = rgb_to_hex([float(p) for p in re.findall(r'[\d.]+', v)[:3]])
        elif v in NAMED:
            v = NAMED[v]
        elif not v.startswith('#'):
            continue
        v = rgb_to_hex(hex_to_rgb(v))
        if v not in found:
            found.append(v)
    return found


# ---------------------------------------------------------------- the logo as an analysis bitmap

class Logo:
    """alpha: ink coverage 0..1 over the analysis region; layers: [(hex, coverage)] per colour.
    Pixel (row, col) has its centre at units (x0 + (col + 0.5) / k, y0 + (row + 0.5) / k)."""

    def __init__(self, path, alpha, layers, k, x0, y0, kind, svg_text=None, background=None):
        self.path, self.alpha, self.layers, self.k, self.x0, self.y0 = Path(path), alpha, layers, k, x0, y0
        self.kind, self.svg_text, self.background = kind, svg_text, background
        self.mask = alpha > 0.5
        ys, xs = np.nonzero(self.mask)
        if len(ys) == 0:
            raise SystemExit('No logo found in the file (is it empty, or is the background not plain?)')
        self.bbox_px = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        bx0, by0 = self.units(xs.min() - 0.5, ys.min() - 0.5)
        bx1, by1 = self.units(xs.max() + 0.5, ys.max() + 0.5)
        self.bbox = (bx0, by0, bx1, by1)
        self.size = max(bx1 - bx0, by1 - by0)          # the larger side of the ink, in units
        self.size_px = self.size * self.k
        self.unit_name = 'units' if kind == 'svg' else 'px'

    @property
    def colours(self):
        return [c for c, _ in self.layers]

    def units(self, col, row):
        return self.x0 + (col + 0.5) / self.k, self.y0 + (row + 0.5) / self.k

    def px(self, x, y):
        return (x - self.x0) * self.k - 0.5, (y - self.y0) * self.k - 0.5


def _split_layers(rgba, colours):
    a = rgba[..., 3].astype(np.float32) / 255
    if len(colours) <= 1:
        return [(colours[0] if colours else '#000000', a)]
    rgb = rgba[..., :3].astype(np.float32)
    pal = np.array([hex_to_rgb(c) for c in colours], np.float32)
    near = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    return [(c, np.where(near == i, a, 0)) for i, c in enumerate(colours)]


def load_logo(path, renderer, target=2000, colours=None, background=None):
    """Render or read the logo so that its larger ink side is about `target` pixels, with a margin around it."""
    path = Path(path)
    if path.suffix.lower() == '.svg':
        text = path.read_text()
        vx, vy, vw, vh = svg_viewbox(text)
        s = 800 / max(vw, vh)
        low = np.asarray(renderer.png(svg_region(text, vx, vy, vw, vh, round(vw * s), round(vh * s)),
                                      round(vw * s), round(vh * s)))[..., 3]
        ys, xs = np.nonzero(low > 5)
        if len(ys) == 0:
            raise SystemExit(f'{path}: nothing visible to measure')
        x0, x1 = vx + xs.min() / s, vx + (xs.max() + 1) / s
        y0, y1 = vy + ys.min() / s, vy + (ys.max() + 1) / s
        size = max(x1 - x0, y1 - y0)
        pad = 0.06 * size
        k = target / size
        rx, ry = x0 - pad, y0 - pad
        rw, rh = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
        wpx, hpx = int(np.ceil(rw * k)), int(np.ceil(rh * k))
        rgba = np.asarray(renderer.png(svg_region(text, rx, ry, wpx / k, hpx / k, wpx, hpx), wpx, hpx))
        named = colours or svg_colours(text)
        ink = rgba[..., 3] > 200
        used = []
        if named and ink.any():
            px = rgba[ink][:, :3].astype(np.float32)
            pal = np.array([hex_to_rgb(c) for c in named], np.float32)
            near = ((px[:, None] - pal[None]) ** 2).sum(-1)
            idx, dist = near.argmin(1), near.min(1)
            for i, c in enumerate(named):
                if (idx == i).mean() > 0.003 and np.median(dist[idx == i]) < 30 ** 2:
                    used.append(c)
        if not used:
            used = [rgb_to_hex(np.median(rgba[ink][:, :3], 0))] if ink.any() else ['#000000']
        return Logo(path, rgba[..., 3].astype(np.float32) / 255, _split_layers(rgba, used), k, rx, ry, 'svg', text)

    img = Image.open(path)
    rgba = np.asarray(img.convert('RGBA')).astype(np.float32)
    H0, W0 = rgba.shape[:2]
    if rgba[..., 3].min() < 250:
        a = rgba[..., 3] / 255
        bg = None
    else:
        rgb = rgba[..., :3]
        border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
        bg = np.array(hex_to_rgb(background), np.float32) if background else np.median(border, 0)
        dist = np.linalg.norm(rgb - bg, axis=-1)
        ink = dist > max(40.0, 0.6 * np.percentile(dist, 99.5))
        logo_col = np.median(rgb[ink], 0) if ink.any() else bg
        v = logo_col - bg
        a = np.clip(((rgb - bg) @ v) / max(float(v @ v), 1e-6), 0, 1)
    k = float(min(4.0, max(1.0, target / max(H0, W0))))
    W, H = int(round(W0 * k)), int(round(H0 * k))
    big = lambda arr: np.asarray(Image.fromarray(arr.astype(np.float32), 'F').resize((W, H), Image.BICUBIC))
    alpha = np.clip(big(a), 0, 1)
    rgb_big = np.stack([big(rgba[..., c]) for c in range(3)], -1)
    rgba_big = np.concatenate([np.clip(rgb_big, 0, 255), (alpha * 255)[..., None]], -1).astype(np.uint8)
    ink = alpha > 0.8
    cols = colours or ([rgb_to_hex(np.median(rgb_big[ink], 0))] if ink.any() else ['#000000'])
    return Logo(path, alpha, _split_layers(rgba_big, cols), k, 0.0, 0.0, 'raster',
                background=rgb_to_hex(bg) if bg is not None else None)


# ---------------------------------------------------------------- annotated images

def font(size):
    return ImageFont.truetype(str(FONT), int(size))


class Canvas:
    """A display copy of the logo (light, so marks stand out) with drawing in analysis-pixel coordinates."""

    def __init__(self, logo, width=1400, tint=(208, 214, 222), ground=(255, 255, 255)):
        self.logo = logo
        h, w = logo.alpha.shape
        self.f = width / w
        self.size = (width, int(round(h * self.f)))
        a = np.asarray(Image.fromarray((logo.alpha * 255).astype(np.uint8)).resize(self.size, Image.LANCZOS)) / 255
        base = np.ones((*self.size[::-1], 3)) * np.array(ground) * (1 - a[..., None]) + np.array(tint) * a[..., None]
        self.img = Image.fromarray(base.astype(np.uint8)).convert('RGBA')
        self.layer = Image.new('RGBA', self.size, (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.layer)

    def p(self, col, row):
        return ((col + 0.5) * self.f, (row + 0.5) * self.f)

    def u(self, x, y):
        """Display position of a point given in logo units."""
        return self.p(*self.logo.px(x, y))

    def circle(self, col, row, r_px, outline, width=2, fill=None):
        x, y = self.p(col, row)
        r = r_px * self.f
        self.d.ellipse((x - r, y - r, x + r, y + r), outline=outline, width=width, fill=fill)

    def line(self, a, b, colour, width=2):
        self.d.line([a, b], fill=colour, width=width)

    def dashed(self, a, b, colour, width=2, dash=10):
        a, b = np.array(a, float), np.array(b, float)
        n = max(1, int(np.linalg.norm(b - a) / dash))
        for i in range(0, n, 2):
            self.d.line([tuple(a + (b - a) * i / n), tuple(a + (b - a) * min(n, i + 1) / n)], fill=colour, width=width)

    def text(self, xy, s, colour=(20, 20, 20), size=22, anchor='la'):
        self.d.text(xy, s, fill=colour, font=font(size), anchor=anchor, stroke_width=3, stroke_fill=(255, 255, 255))

    def save(self, path, caption=None):
        out = Image.alpha_composite(self.img, self.layer).convert('RGB')
        if caption:
            out = add_caption(out, caption)
        out.save(path, optimize=True)
        return path


def add_caption(img, caption, size=24):
    lines = caption if isinstance(caption, list) else [caption]
    pad = 18
    h = pad * 2 + len(lines) * int(size * 1.45)
    out = Image.new('RGB', (img.width, img.height + h), (255, 255, 255))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    for i, line in enumerate(lines):
        d.text((pad, img.height + pad + i * int(size * 1.45)), line, fill=(40, 40, 40), font=font(size))
    return out


GREEN, AMBER, RED, BLUE, GREY = (22, 150, 90, 255), (225, 140, 0, 255), (220, 30, 40, 255), (40, 110, 230, 255), (90, 90, 90, 255)


def safe_output_dir(path, force=False):
    path = Path(path)
    if path.exists() and any(path.iterdir()) and not force:
        raise SystemExit(f'{path} already has files. Choose a new folder, or pass --force after backing it up.')
    path.mkdir(parents=True, exist_ok=True)
    return path

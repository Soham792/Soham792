"""Shared helpers for the animated-README generator.

Rules baked in here (GitHub strips JS and blocks network loads in <img> SVGs):
  * only CSS + SMIL animation
  * every font / image is inlined as base64 (woff2 / PNG / JPEG)
  * SMIL timelines start at begin="0s" and use keyTimes for delays
  * base attribute values are the FINISHED state, so a renderer that ignores
    animation still shows the completed card
  * ids and class names are namespaced per file via the prefix `p`
"""
import base64, io, json, math, pathlib
from xml.sax.saxutils import escape as _esc

ROOT = pathlib.Path(__file__).resolve().parent
BG, CY, VI, PK = "#0d0e16", "#22d3ee", "#a78bfa", "#f472b6"
TX, MU, DIM = "#e8eaf6", "#8b90a8", "#5b6078"
SG = "'PSG','Space Grotesk',ui-sans-serif,system-ui,sans-serif"
JB = "'PJB','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace"
ICONS = json.loads((ROOT / "icons.json").read_text())


# ----------------------------------------------------------------- basics
def esc(s):
    return _esc(str(s), {'"': "&quot;"})


def fnum(v):
    if isinstance(v, float):
        s = f"{v:.3f}".rstrip("0").rstrip(".")
        return s if s not in ("", "-0") else "0"
    return str(v)


def load_cfg():
    cfg = json.loads((ROOT / "config.json").read_text())
    u = dict(username=cfg["username"], email=cfg["email"], name=cfg["name"])

    def fill(o):
        if isinstance(o, str):
            for k, v in u.items():
                o = o.replace("{" + k + "}", v)
            return o
        if isinstance(o, list):
            return [fill(i) for i in o]
        if isinstance(o, dict):
            return {k: fill(v) for k, v in o.items()}
        return o
    return fill(cfg)


def b64(path):
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def png_uri(im, max_w, colors=160):
    """Resize an RGBA PIL image to max_w and return a quantised PNG data-URI + size."""
    from PIL import Image
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    q = im.quantize(colors=colors, method=Image.FASTOCTREE, dither=Image.NONE)
    buf = io.BytesIO()
    q.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


def est_w(text, size, mono=False):
    return len(text) * size * (0.6 if mono else 0.545)


def fit(text, max_w, base, mono=False, floor=10):
    w = est_w(text, base, mono)
    return base if w <= max_w else max(floor, base * max_w / w)


# ----------------------------------------------------------------- document
def font_css():
    f = ROOT / "fonts"
    face = lambda fam, wt, fn: (
        f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:normal;"
        f"src:url(data:font/woff2;base64,{b64(f / fn)}) format('woff2');}}")
    return (face("PSG", 500, "sg500.woff2") + face("PSG", 700, "sg700.woff2")
            + face("PJB", 400, "jb400.woff2") + face("PJB", 600, "jb600.woff2"))


def svg_doc(p, w, h, body, defs="", css="", title="", desc=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{p}-t {p}-d">'
            f'<title id="{p}-t">{esc(title)}</title><desc id="{p}-d">{esc(desc)}</desc>'
            f'<style>{font_css()}'
            f"@keyframes {p}-rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}"
            f"@keyframes {p}-pop{{from{{opacity:0;transform:scale(.86)}}to{{opacity:1;transform:none}}}}"
            f".{p}-in{{animation:{p}-rise .9s cubic-bezier(.2,.7,.2,1) both}}"
            f".{p}-pop{{animation:{p}-pop .7s cubic-bezier(.2,.9,.3,1.2) both;transform-box:fill-box;transform-origin:center}}"
            f".{p}-sg{{font-family:{SG}}}.{p}-jb{{font-family:{JB}}}"
            f"{css}</style><defs>{base_defs(p)}{defs}</defs>{body}</svg>")


def base_defs(p):
    return (
        f'<linearGradient id="{p}-aur" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/>'
        f'<stop offset=".5" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient>'
        f'<linearGradient id="{p}-aurd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CY}"/>'
        f'<stop offset=".5" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient>'
        f'<linearGradient id="{p}-hair" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CY}" stop-opacity=".6"/>'
        f'<stop offset=".5" stop-color="{VI}" stop-opacity=".16"/><stop offset="1" stop-color="{PK}" stop-opacity=".55"/></linearGradient>'
        f'<linearGradient id="{p}-glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".06"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity=".008"/></linearGradient>'
        f'<pattern id="{p}-dots" width="12" height="12" patternUnits="userSpaceOnUse">'
        f'<circle cx="1.5" cy="1.5" r=".9" fill="#c4b5fd" opacity=".17"/></pattern>'
        f'<filter id="{p}-blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>'
        f'<filter id="{p}-blur40" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>')


def card(p, k, x, y, w, h, r=22):
    """Midnight-glass card: dark base, glass sheen, dot texture, gradient hairline."""
    return (f'<g id="{p}-card-{k}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{BG}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{p}-glass)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{p}-dots)"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" '
            f'stroke="url(#{p}-hair)" stroke-width="1"/></g>')


def clip(p, k, x, y, w, h, r=22):
    return f'<clipPath id="{p}-clip-{k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>'


# ----------------------------------------------------------------- SMIL
def A(attr, vals, kt=None, dur=1.0, begin="0s", rep=False, spl=None, calc=None, tag="animate", typ=None, extra=""):
    s = f'<{tag} attributeName="{attr}" '
    if typ:
        s += f'type="{typ}" '
    s += f'values="{";".join(str(v) for v in vals)}" dur="{fnum(float(dur))}s" begin="{begin}" '
    if kt:
        s += f'keyTimes="{";".join(fnum(float(k)) for k in kt)}" '
    if calc:
        s += f'calcMode="{calc}" '
    if spl:
        s += f'keySplines="{spl}" '
    s += 'repeatCount="indefinite"' if rep else 'fill="freeze"'
    return s + f" {extra}/>"


EASE = "0.16 0.84 0.3 1"


def ENTER(attr, a, b, delay, dur, tag="animate", typ=None, ease=True):
    """One-shot entrance. Timeline starts at 0s; the delay is a held first keyframe,
    so the element's own (base) value -- the finished state -- is what a static renderer shows."""
    if delay <= 0:
        return A(attr, [a, b], [0, 1], dur, calc="spline" if ease else None,
                 spl=EASE if ease else None, tag=tag, typ=typ)
    tot = delay + dur
    return A(attr, [a, a, b], [0, delay / tot, 1], tot, calc="spline" if ease else None,
             spl=f"0 0 1 1;{EASE}" if ease else None, tag=tag, typ=typ)


def DRAW(delay, dur=0.9):
    """stroke-draw-in for elements that carry pathLength="1" stroke-dasharray="1"."""
    return ENTER("stroke-dashoffset", 1, 0, delay, dur, ease=True)


def CYCLE(i, n, total, fade=0.35, rise=8, axis="y"):
    """Slot i of n in a looping carousel/cycle of `total` seconds. Returns (opacity, translate) SMIL.
    Slot 0 is visible at t=0 (it is also the finished/base state)."""
    s = total / n
    a, b = i * s, (i + 1) * s
    f = min(fade, s / 3)
    pts = [(0, 0)]
    if i == 0:
        kt = [0, (b - f) / total, b / total, (total - f) / total, 1]
        op = [1, 1, 0, 0, 1]
        ty = [0, 0, -rise, rise, 0]
    else:
        kt = [0, a / total, (a + f) / total, (b - f) / total, b / total, 1]
        op = [0, 0, 1, 1, 0, 0]
        ty = [rise, rise, 0, 0, -rise, -rise]
    o = A("opacity", op, kt, total, rep=True)
    fmt = (lambda v: f"0 {v}") if axis == "y" else (lambda v: f"{v} 0")
    t = A("transform", [fmt(v) for v in ty], kt, total, rep=True, tag="animateTransform", typ="translate")
    return o, t


def sparkle(cx, cy, r, fill, p, delay=0.0, dur=2.6, op=0.9):
    """4-point twinkle star."""
    k = r * 0.22
    d = (f"M{cx} {cy - r} Q{cx + k} {cy - k} {cx + r} {cy} Q{cx + k} {cy + k} {cx} {cy + r} "
         f"Q{cx - k} {cy + k} {cx - r} {cy} Q{cx - k} {cy - k} {cx} {cy - r}Z")
    kt = [0, .5, 1]
    return (f'<path d="{d}" fill="{fill}" opacity="{op}"><animate attributeName="opacity" values="{op};0.15;{op}" '
            f'keyTimes="0;.5;1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="scale" additive="sum" values="1;.7;1" keyTimes="0;.5;1" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></path>')


# ----------------------------------------------------------------- icons
# Lucide-style 24x24 stroke icons (hand-set paths; checked visually in QA)
LI = {
    "pin": ["M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z", "M12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"],
    "building": ["M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z", "M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2",
                 "M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2", "M10 6h4M10 10h4M10 14h4M10 18h4"],
    "star": ["M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"],
    "repo": ["M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"],
    "arrow": ["M5 12h14", "M13 5l7 7-7 7"],
    "mail": ["M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z", "M22 7l-8.97 5.7a2 2 0 0 1-2.06 0L2 7"],
    "lock": ["M5 11h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z", "M7 11V7a5 5 0 0 1 10 0v4"],
    "code": ["M16 18l6-6-6-6", "M8 6l-6 6 6 6"],
    "sparkles": ["M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z", "M19 15l.7 1.8 1.8.7-1.8.7L19 20l-.7-1.8-1.8-.7 1.8-.7z"],
    "rocket": ["M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z",
               "M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z",
               "M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0", "M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"],
    "camera": ["M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z", "M12 10a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"],
    "gamepad": ["M6 11h4M8 9v4M15 12h.01M18 10h.01",
                "M17.32 5H6.68a4 4 0 0 0-3.98 3.59C2.6 9.42 2 14.46 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.41-1.41A2 2 0 0 1 9.83 16h4.34a2 2 0 0 1 1.41.59L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.55-.6-6.58-.69-7.26A4 4 0 0 0 17.32 5z"],
    "bike": ["M5.5 14a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z", "M18.5 14a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z",
             "M15 3.5a1 1 0 1 0 0 2 1 1 0 0 0 0-2z", "M12 17.5V14l-3-3 4-3 2 3h2"],
    "headphones": ["M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"],
    "mountain": ["M8 3l4 8 5-5 5 15H2z"],
    "book": ["M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z", "M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"],
    "coffee": ["M10 2v2M14 2v2M6 2v2", "M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1"],
    "cpu": ["M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z", "M9 9h6v6H9z",
            "M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"],
    "layers": ["M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z",
               "M22 17.65l-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65", "M22 12.65l-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"],
    "music": ["M9 18V5l12-2v13", "M6 15a3 3 0 1 0 0 6 3 3 0 0 0 0-6z", "M18 13a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"],
    "activity": ["M22 12h-4l-3 9L9 3l-3 9H2"],
    "users": ["M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2", "M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M22 21v-2a4 4 0 0 0-3-3.87", "M16 3.13a4 4 0 0 1 0 7.75"],
    "git": ["M6 3v12", "M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M18 9a9 9 0 0 1-9 9"],
    "headset": ["M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"],
}


def li(name, x, y, size, color, sw=1.8, extra="", pl=False, delay=0.0):
    """Line icon placed at (x, y) with box `size`. pl=True -> paths draw in (pathLength=1)."""
    s = size / 24
    paths = ""
    for i, d in enumerate(LI[name]):
        if pl:
            paths += (f'<path d="{d}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0">'
                      f'{DRAW(delay + i * 0.12)}</path>')
        else:
            paths += f'<path d="{d}"/>'
    return (f'<g transform="translate({fnum(float(x))} {fnum(float(y))}) scale({fnum(float(s))})" fill="none" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}>{paths}</g>')


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def si(name, x, y, size, color=None, extra=""):
    """Simple Icons glyph (24x24 grid) at (x, y). Brand colour; near-black brands are lifted for the dark UI."""
    ic = ICONS[name]
    c = color or ("#" + ic["hex"])
    if color is None and lum(ic["hex"]) < 0.22:
        c = "#e5e7eb"
    s = size / 24
    return (f'<path transform="translate({fnum(float(x))} {fnum(float(y))}) scale({fnum(float(s))})" '
            f'd="{ic["path"]}" fill="{c}" {extra}/>')


def si_title(name):
    return ICONS[name]["title"]

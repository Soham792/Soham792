from lib import *
from PIL import Image

P = "a"
W, H = 900, 480
CW = 436


def scene(k, ix, iy, iw, ih, hb):
    pairs = [(CY, VI), (VI, PK), (PK, CY), (CY, PK)]
    c1, c2 = pairs[k % 4]
    cx, cy = ix + iw / 2, iy + ih / 2 + 8
    d = (f'<linearGradient id="{P}-sg{k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}" stop-opacity=".5"/>'
         f'<stop offset="1" stop-color="{c2}" stop-opacity=".18"/></linearGradient>'
         f'<radialGradient id="{P}-sr{k}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c1}" stop-opacity=".55"/>'
         f'<stop offset="1" stop-color="{c1}" stop-opacity="0"/></radialGradient>')
    g = (f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="{BG}"/>'
         f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="url(#{P}-sg{k})"/>'
         f'<circle cx="{cx}" cy="{cy}" r="150" fill="url(#{P}-sr{k})"/>'
         f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="url(#{P}-dots)" opacity=".8"/>'
         f'<circle cx="{cx}" cy="{cy}" r="86" fill="none" stroke="#fff" stroke-opacity=".12" stroke-dasharray="3 7">'
         f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></circle>'
         f'<circle cx="{cx}" cy="{cy}" r="64" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-opacity=".28"/>'
         f'<g>{A("transform", ["0 0", "0 -7", "0 0"], [0, .5, 1], 4.5, rep=True, tag="animateTransform", typ="translate", calc="spline", spl="0.4 0 0.6 1;0.4 0 0.6 1")}'
         f'{li(hb["icon"], cx - 36, cy - 36, 72, "#ffffff", 1.35)}</g>')
    for j, (dx, dy, r, c) in enumerate([(-125, -50, 8, c1), (118, -62, 6, c2), (104, 56, 9, "#ffffff"), (-110, 62, 5, c2)]):
        g += sparkle(cx + dx, cy + dy, r, c, P, delay=j * .7)
    return d, g


def build(cfg):
    d, b = "", ""
    # ============================================================ LEFT CARD
    b += card(P, "l", 0, 0, CW, H, 24)
    wx, wy, ww, wh = 22, 22, 392, 238
    d += clip(P, "win", wx, wy, ww, wh, 14)
    b += (f'<g class="{P}-in" style="animation-delay:.1s"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="#0a0b12"/>'
          f'<rect x="{wx + .5}" y="{wy + .5}" width="{ww - 1}" height="{wh - 1}" rx="13.5" fill="none" stroke="#fff" stroke-opacity=".1"/>'
          f'<rect x="{wx}" y="{wy}" width="{ww}" height="34" rx="14" fill="#fff" fill-opacity=".04"/>'
          f'<circle cx="{wx + 18}" cy="{wy + 17}" r="4.5" fill="{PK}"/><circle cx="{wx + 33}" cy="{wy + 17}" r="4.5" fill="{VI}"/><circle cx="{wx + 48}" cy="{wy + 17}" r="4.5" fill="{CY}"/>'
          f'<rect x="{wx + 70}" y="{wy + 6}" width="{ww - 86}" height="22" rx="11" fill="#fff" fill-opacity=".06"/>'
          f'{li("lock", wx + 80, wy + 11, 12, MU, 2)}')
    url = f'github.com/{cfg["username"]}'
    uw = len(url) * 6.6
    n = len(url)
    TT = 3.0
    tk = [0] + [(.5 + 1.8 * (k - 1) / n) / TT for k in range(1, n + 1)]
    d += (f'<clipPath id="{P}-urlclip"><rect x="{wx + 98}" y="{wy + 8}" width="{uw:.1f}" height="18">'
          f'{A("width", [0] + [round(6.6 * k, 1) for k in range(1, n + 1)], tk, TT, calc="discrete")}</rect></clipPath>')
    b += (f'<text x="{wx + 98}" y="{wy + 21.5}" class="{P}-jb" font-size="11" fill="{TX}" textLength="{uw:.1f}" lengthAdjust="spacing" clip-path="url(#{P}-urlclip)">{esc(url)}</text>'
          f'<rect x="{wx + 98 + uw + 2:.1f}" y="{wy + 10}" width="6" height="14" rx="1" fill="{CY}">'
          f'{A("x", [wx + 99] + [round(wx + 98 + 6.6 * k + 1, 1) for k in range(1, n + 1)], tk, TT, calc="discrete")}'
          f'<animate attributeName="opacity" values="1;0" keyTimes="0;.5" dur="1s" begin="{TT}s" repeatCount="indefinite" calcMode="discrete"/></rect></g>')
    # viewport: aurora scene + code lines + character
    vy = wy + 34
    vh = wh - 34
    b += f'<g clip-path="url(#{P}-clip-win)">'
    b += (f'<rect x="{wx}" y="{vy}" width="{ww}" height="{vh}" fill="url(#{P}-vg)"/>'
          f'<circle cx="{wx + 300}" cy="{vy + 100}" r="130" fill="url(#{P}-vr)"/>'
          f'<rect x="{wx}" y="{vy}" width="{ww}" height="{vh}" fill="url(#{P}-dots)" opacity=".7"/>')
    d += (f'<linearGradient id="{P}-vg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VI}" stop-opacity=".22"/>'
          f'<stop offset="1" stop-color="{CY}" stop-opacity=".08"/></linearGradient>'
          f'<radialGradient id="{P}-vr" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{PK}" stop-opacity=".4"/><stop offset="1" stop-color="{PK}" stop-opacity="0"/></radialGradient>')
    code = [(0, 70, CY), (14, 110, VI), (14, 84, PK), (28, 120, CY), (28, 64, MU), (14, 40, VI), (0, 56, PK)]
    for i, (ind, w_, c) in enumerate(code):
        y = vy + 22 + i * 19
        b += (f'<text x="{wx + 14}" y="{y + 8}" class="{P}-jb" font-size="9" fill="{DIM}">{i + 1:02d}</text>'
              f'<rect x="{wx + 38 + ind}" y="{y}" width="{w_}" height="9" rx="4.5" fill="{c}" opacity=".78">'
              f'{ENTER("width", 0, w_, .7 + i * .22, .6)}</rect>')
    # status chip
    b += (f'<g class="{P}-in" style="animation-delay:1.9s"><rect x="{wx + 14}" y="{vy + vh - 34}" width="130" height="22" rx="11" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-opacity=".12"/>'
          f'<circle cx="{wx + 28}" cy="{vy + vh - 23}" r="3.5" fill="{CY}">{A("opacity", [1, .25, 1], [0, .5, 1], 1.8, rep=True)}</circle>'
          f'<text x="{wx + 38}" y="{vy + vh - 19}" class="{P}-jb" font-size="10" fill="{TX}">build passing</text></g>')
    src = Image.open(ROOT / "img" / "laptop_src.png")
    uri, (iw_, ih_) = png_uri(src, 330, 170)
    cwid = 156
    chh = cwid * ih_ / iw_
    b += (f'<g class="{P}-in" style="animation-delay:.5s"><image x="{wx + ww - cwid - 8}" y="{vy + vh - chh + 20:.1f}" width="{cwid}" height="{chh:.1f}" '
          f'xlink:href="{uri}"/></g></g>')

    # capability rows
    for i, cap in enumerate(cfg["capabilities"][:3]):
        y = 282 + i * 64
        b += (f'<g class="{P}-in" style="animation-delay:{.9 + i * .15:.2f}s">'
              f'<rect x="22" y="{y}" width="392" height="54" rx="14" fill="#fff" fill-opacity=".035"/>'
              f'<rect x="22.5" y="{y + .5}" width="391" height="53" rx="13.5" fill="none" stroke="#fff" stroke-opacity=".08"/>'
              f'<rect x="32" y="{y + 7}" width="40" height="40" rx="12" fill="url(#{P}-aurd)" fill-opacity=".16"/>'
              f'<rect x="32.5" y="{y + 7.5}" width="39" height="39" rx="11.5" fill="none" stroke="url(#{P}-hair)"/>'
              f'{li(cap["icon"], 42, y + 17, 20, "url(#" + P + "-aurd)", 1.9)}'
              f'<text x="86" y="{y + 24}" class="{P}-sg" font-size="15.5" font-weight="700" fill="{TX}">{esc(cap["title"])}</text>'
              f'<text x="86" y="{y + 42}" class="{P}-sg" font-size="12.5" font-weight="500" fill="{MU}">{esc(cap["sub"])}</text>'
              f'<g>{A("transform", ["0 0", "5 0", "0 0"], [0, .5, 1], 2.4, begin="0s", rep=True, tag="animateTransform", typ="translate", calc="spline", spl="0.4 0 0.6 1;0.4 0 0.6 1")}'
              f'{li("arrow", 384, y + 19, 16, MU, 2)}</g></g>')

    # ============================================================ RIGHT CARD
    RX = 464
    b += card(P, "r", RX, 0, CW, H, 24)
    hb = cfg["hobbies"][:4]
    nh = len(hb)
    SLOT = 4.0
    TOT = SLOT * nh
    ix, iy, iw, ih = RX + 22, 22, 392, 226
    d += clip(P, "img", ix, iy, iw, ih, 16)
    b += f'<g clip-path="url(#{P}-clip-img)">'
    for k, h_ in enumerate(hb):
        sd, sg = scene(k, ix, iy, iw, ih, h_)
        d += sd
        o, t = CYCLE(k, nh, TOT, fade=.6, rise=26, axis="x")
        b += f'<g opacity="{1 if k == 0 else 0}">{o}{t}{sg}</g>'
    # dark top scrim for the progress bars
    d += (f'<linearGradient id="{P}-scrim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".5"/>'
          f'<stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>')
    b += f'<rect x="{ix}" y="{iy}" width="{iw}" height="70" fill="url(#{P}-scrim)"/>'
    # Instagram-style segmented progress
    gap = 6
    segw = (iw - 28 - gap * (nh - 1)) / nh
    for k in range(nh):
        sx = ix + 14 + k * (segw + gap)
        kt = [0, k / nh, (k + 1) / nh, 1]
        b += (f'<rect x="{sx:.1f}" y="{iy + 14}" width="{segw:.1f}" height="3.5" rx="1.75" fill="#fff" fill-opacity=".28"/>'
              f'<rect x="{sx:.1f}" y="{iy + 14}" width="{segw if k == 0 else 0:.1f}" height="3.5" rx="1.75" fill="#fff">'
              f'{A("width", [0, 0, round(segw, 1), round(segw, 1)], kt, TOT, rep=True)}</rect>')
    # counter chips
    for k in range(nh):
        o, _ = CYCLE(k, nh, TOT, fade=.4)
        b += (f'<text x="{ix + 16}" y="{iy + 38}" class="{P}-jb" font-size="10.5" font-weight="600" fill="#fff" opacity="{1 if k == 0 else 0}" letter-spacing="1">'
              f'{o}{k + 1:02d} / {nh:02d}</text>')
    b += "</g>"
    b += (f'<rect x="{ix + .5}" y="{iy + .5}" width="{iw - 1}" height="{ih - 1}" rx="15.5" fill="none" stroke="#fff" stroke-opacity=".12"/>')
    # captions
    for k, h_ in enumerate(hb):
        o, t = CYCLE(k, nh, TOT, fade=.45, rise=8)
        b += (f'<g opacity="{1 if k == 0 else 0}">{o}{t}'
              f'<text x="{ix + 2}" y="276" class="{P}-sg" font-size="19" font-weight="700" fill="{TX}">{esc(h_["title"])}</text>'
              f'<text x="{ix + 2}" y="298" class="{P}-sg" font-size="{fit(h_["caption"], 388, 13.5):.1f}" font-weight="500" fill="{MU}">{esc(h_["caption"])}</text></g>')
    # daily rings
    b += (f'<line x1="{ix}" y1="318" x2="{ix + iw}" y2="318" stroke="#fff" stroke-opacity=".08"/>'
          f'<text x="{ix + 2}" y="341" class="{P}-jb" font-size="10.5" fill="{DIM}" letter-spacing="2">DAILY RINGS</text>')
    RT = 8.0
    for k, r_ in enumerate(cfg["rings"][:3]):
        cx = ix + iw * (2 * k + 1) / 6
        cy, rr = 394, 30
        C = 2 * math.pi * rr
        fin = C * (1 - r_["pct"])
        s0 = .04 + .05 * k
        kt = [0, s0, s0 + .34, .9, 1]
        vals = [f"{C:.1f}", f"{C:.1f}", f"{fin:.1f}", f"{fin:.1f}", f"{C:.1f}"]
        b += (f'<g class="{P}-in" style="animation-delay:{1.0 + k * .15:.2f}s">'
              f'<circle cx="{cx:.1f}" cy="{cy}" r="{rr}" fill="none" stroke="#fff" stroke-opacity=".08" stroke-width="7"/>'
              f'<circle cx="{cx:.1f}" cy="{cy}" r="{rr}" fill="none" stroke="{r_["color"]}" stroke-width="7" stroke-linecap="round" '
              f'stroke-dasharray="{C:.1f}" stroke-dashoffset="{fin:.1f}" transform="rotate(-90 {cx:.1f} {cy})">'
              f'{A("stroke-dashoffset", vals, kt, RT, rep=True, calc="spline", spl="0 0 1 1;0.3 0.6 0.3 1;0 0 1 1;0.5 0 0.8 0.5")}</circle>'
              f'<text x="{cx:.1f}" y="{cy + 4.5}" text-anchor="middle" class="{P}-jb" font-size="13" font-weight="600" fill="{TX}">{round(r_["pct"] * 100)}%</text>'
              f'<text x="{cx:.1f}" y="{cy + 54}" text-anchor="middle" class="{P}-sg" font-size="12.5" font-weight="500" fill="{MU}">{esc(r_["label"])}</text></g>')
    return svg_doc(P, W, H, b, d, "", f'{cfg["name"]} - about & life',
                   "Left: browser window with a developer portrait and three capability rows. Right: hobby carousel with progress bars and three daily rings.")

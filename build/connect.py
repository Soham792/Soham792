from lib import *
from PIL import Image

P = "c"
W, H = 900, 380


def build(cfg):
    d, b = "", ""
    b += card(P, "bg", 0, 0, W, H, 26)
    d += clip(P, "bg", 0, 0, W, H, 26)
    d += (f'<radialGradient id="{P}-halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{VI}" stop-opacity=".55"/>'
          f'<stop offset=".6" stop-color="{CY}" stop-opacity=".18"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></radialGradient>'
          f'<filter id="{P}-neon" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="5"/></filter>')
    b += (f'<g clip-path="url(#{P}-clip-bg)"><ellipse cx="120" cy="215" rx="190" ry="170" fill="url(#{P}-halo)">'
          f'{A("opacity", [.8, 1, .8], [0, .5, 1], 5, rep=True)}</ellipse>'
          f'<g filter="url(#{P}-blur40)" opacity=".5"><ellipse cx="780" cy="330" rx="170" ry="70" fill="{PK}" opacity=".35"/></g></g>')

    # pointing character (floats gently)
    src = Image.open(ROOT / "img" / "pointing_src.png")
    uri, (iw, ih) = png_uri(src, 330, 200)
    ch = 336
    cw = ch * iw / ih
    cx0, cy0 = 30, 22
    b += (f'<g class="{P}-in" style="animation-delay:.1s"><g>'
          f'{A("transform", ["0 0", "0 -5", "0 0"], [0, .5, 1], 4.8, rep=True, tag="animateTransform", typ="translate", calc="spline", spl="0.4 0 0.6 1;0.4 0 0.6 1")}'
          f'<image x="{cx0}" y="{cy0}" width="{cw:.1f}" height="{ch}" xlink:href="{uri}"/></g></g>')
    tipx, tipy = cx0 + cw * .985, cy0 + ch * .272          # fingertip -> where the neon handle starts

    # neon handle
    handle = "@" + cfg["username"]
    fs = fit(handle, 185, 30)
    hx, hy = tipx + 20, tipy + 4
    d += (f'<linearGradient id="{P}-nstroke" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".5" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/></linearGradient>')
    b += (f'<g class="{P}-in" style="animation-delay:.6s">'
          f'<text x="{hx:.1f}" y="{hy:.1f}" class="{P}-sg" font-size="{fs:.1f}" font-weight="700" fill="url(#{P}-nstroke)" filter="url(#{P}-neon)">{esc(handle)}'
          f'{A("opacity", [1, .55, 1], [0, .5, 1], 3.2, rep=True)}</text>'
          f'<text x="{hx:.1f}" y="{hy:.1f}" class="{P}-sg" font-size="{fs:.1f}" font-weight="700" fill="#fff" stroke="url(#{P}-nstroke)" stroke-width=".8" paint-order="stroke">{esc(handle)}</text>'
          f'<text x="{hx:.1f}" y="{hy + 28:.1f}" class="{P}-jb" font-size="11.5" fill="{MU}" letter-spacing=".5">let\'s build something together</text></g>')
    for (sx, sy, r, c, dl) in [(hx - 6, hy - 44, 8, CY, 0), (hx + 120, hy - 54, 6, PK, .8), (hx + 205, hy - 22, 9, VI, 1.5), (hx + 40, hy + 52, 6, CY, 2.1)]:
        b += sparkle(sx, sy, r, c, P, dl)
    # dashed lead-in pointing from the handle toward the cards
    b += (f'<path d="M{hx:.0f} {hy + 74:.0f} C {hx + 60:.0f} {hy + 120:.0f}, {hx + 130:.0f} {hy + 130:.0f}, 436 {H - 110}" fill="none" '
          f'stroke="url(#{P}-aur)" stroke-opacity=".55" stroke-width="1.6" stroke-dasharray="3 7">{A("stroke-dashoffset", [0, -40], [0, 1], 2.5, rep=True)}</path>')

    # link cards
    links = cfg["links"][:4]
    cx_, cw_, rh, gap = 440, 426, 70, 12
    top = (H - (len(links) * rh + (len(links) - 1) * gap)) / 2
    for i, lk in enumerate(links):
        y = top + i * (rh + gap)
        ic = lk["icon"]
        brand = "#" + ICONS[ic]["hex"]
        if lum(ICONS[ic]["hex"]) < .22:
            brand = "#e5e7eb"
        s = (i * .22) / 2.8
        nud = A("transform", ["0 0", "0 0", "7 0", "0 0", "0 0"], [0, s, s + .06, s + .16, 1], 2.8, rep=True, tag="animateTransform", typ="translate")
        b += (f'<g class="{P}-in" style="animation-delay:{.35 + i * .12:.2f}s">'
              f'<rect x="{cx_}" y="{y}" width="{cw_}" height="{rh}" rx="18" fill="#fff" fill-opacity=".04"/>'
              f'<rect x="{cx_ + .5}" y="{y + .5}" width="{cw_ - 1}" height="{rh - 1}" rx="17.5" fill="none" stroke="url(#{P}-hair)"/>'
              f'<rect x="{cx_ + 14}" y="{y + 13}" width="44" height="44" rx="13" fill="{BG}"/>'
              f'<rect x="{cx_ + 14}" y="{y + 13}" width="44" height="44" rx="13" fill="{brand}" fill-opacity=".12"/>'
              f'<rect x="{cx_ + 14.5}" y="{y + 13.5}" width="43" height="43" rx="12.5" fill="none" stroke="{brand}" stroke-opacity=".4"/>'
              f'{si(ic, cx_ + 25, y + 24, 22)}'
              f'<text x="{cx_ + 74}" y="{y + 31}" class="{P}-sg" font-size="17" font-weight="700" fill="{TX}">{esc(lk["label"])}</text>'
              f'<text x="{cx_ + 74}" y="{y + 50}" class="{P}-jb" font-size="{fit(lk["handle"], 250, 12, True):.1f}" fill="{MU}">{esc(lk["handle"])}</text>'
              f'<g>{nud}{li("arrow", cx_ + cw_ - 46, y + 25, 20, VI, 2.2)}</g></g>')
    return svg_doc(P, W, H, b, d, "", f'Connect with {cfg["name"]}',
                   "The pointing character beside link cards for GitHub, LinkedIn, X and email."), {}

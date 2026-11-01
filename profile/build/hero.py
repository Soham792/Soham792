from lib import *
import base64
from clip import get_frames

P = "h"
W, H = 900, 380
FX, FY, FW, FH = 556, 30, 300, 316          # video window (inside the viewfinder)


def build(cfg):
    px = 2                                    # render frames at 2x for crisp video
    frames, fps, synthetic = get_frames(cfg, round(FW * 1.47), round(FH * 1.47))
    N = len(frames)
    dt = 1.0 / fps
    clip_dur = N * dt
    L = round(clip_dur + 1.4 + 0.4, 2)        # play once, hold ~1.4s, fade, repeat
    X0 = 44
    d = ""                                    # defs
    b = ""                                    # body

    # ------------------------------------------------------------ card + aurora
    b += card(P, "bg", 0, 0, W, H, 26)
    d += clip(P, "bg", 0, 0, W, H, 26)
    blobs = [(180, 70, 190, CY, .20, 14), (560, 330, 220, VI, .22, 18), (820, 70, 170, PK, .20, 16)]
    g = ""
    for i, (cx, cy, r, c, o, sp) in enumerate(blobs):
        g += (f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * .6:.0f}" fill="{c}" opacity="{o}">'
              f'{A("cx", [cx, cx + 40, cx], [0, .5, 1], sp, rep=True)}</ellipse>')
    b += f'<g clip-path="url(#{P}-clip-bg)"><g filter="url(#{P}-blur40)">{g}</g></g>'

    # ------------------------------------------------------------ video (edges melt into the card)
    d += (f'<filter id="{P}-vb" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="17"/></filter>'
          f'<mask id="{P}-vmask" maskUnits="userSpaceOnUse" x="{FX - 20}" y="{FY - 20}" width="{FW + 40}" height="{FH + 40}">'
          f'<rect x="{FX + 20}" y="{FY + 18}" width="{FW - 40}" height="{FH - 36}" rx="34" fill="#fff" filter="url(#{P}-vb)"/></mask>')
    kt_fade = [0, .12 / L, (L - .45) / L, (L - .05) / L, 1]
    fr = ""
    for i, jpg in enumerate(frames):
        a, bb = i * dt / L, (i + 1) * dt / L
        if N == 1:
            anim = ""
        elif i == 0:
            anim = A("opacity", [1, 0], [0, bb], L, rep=True, calc="discrete")
        elif i == N - 1:
            anim = A("opacity", [0, 1], [0, a], L, rep=True, calc="discrete")
        else:
            anim = A("opacity", [0, 1, 0], [0, a, bb], L, rep=True, calc="discrete")
        fr += (f'<image x="{FX}" y="{FY}" width="{FW}" height="{FH}" preserveAspectRatio="xMidYMid slice" '
               f'xlink:href="data:image/jpeg;base64,{base64.b64encode(jpg).decode()}">{anim}</image>')
    # glass sheen + aurora glow are re-applied OVER the video (inside the same mask) so its flat background
    # matches the glowing card around it exactly: no visible seam
    b += (f'<g mask="url(#{P}-vmask)"><g>{A("opacity", [0, 1, 1, 0, 0], kt_fade, L, rep=True)}{fr}'
          f'<rect x="0" y="0" width="{W}" height="{H}" rx="26" fill="url(#{P}-glass)"/>'
          f'<g clip-path="url(#{P}-clip-bg)"><g filter="url(#{P}-blur40)">{g}</g></g></g></g>')
    b += f'<rect x="12" y="12" width="{W - 24}" height="{H - 24}" rx="22" fill="url(#{P}-dots)" opacity=".55"/>'

    # ------------------------------------------------------------ viewfinder chrome
    bx, by, bw, bh, ln = FX - 6, FY - 6, FW + 12, FH + 12, 30
    corners = [f"M{bx} {by + ln}V{by}H{bx + ln}", f"M{bx + bw - ln} {by}H{bx + bw}V{by + ln}",
               f"M{bx} {by + bh - ln}V{by + bh}H{bx + ln}", f"M{bx + bw - ln} {by + bh}H{bx + bw}V{by + bh - ln}"]
    for i, c in enumerate(corners):
        b += (f'<path d="{c}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0" fill="none" '
              f'stroke="url(#{P}-aurd)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
              f'{DRAW(0.25 + i * .16, .8)}</path>')
    # REC + filename
    b += (f'<g class="{P}-in" style="animation-delay:1.1s">'
          f'<circle cx="{FX + 20}" cy="{FY + 22}" r="4.6" fill="{PK}">'
          f'{A("opacity", [1, .12], [0, .5], 1.3, rep=True, calc="discrete")}</circle>'
          f'<text x="{FX + 31}" y="{FY + 26}" class="{P}-jb" font-size="11" font-weight="600" fill="{PK}" letter-spacing="1.5">REC</text>'
          f'<text x="{FX + FW - 14}" y="{FY + 26}" text-anchor="end" class="{P}-jb" font-size="10.5" fill="{MU}">intro_take01.mov</text></g>')
    # scrubber synced to the loop
    sx, sy, sw = FX + 20, FY + FH - 24, FW - 40
    kt_s = [0, clip_dur / L, (L - .05) / L, 1]
    b += (f'<g class="{P}-in" style="animation-delay:1.2s">'
          f'<rect x="{sx}" y="{sy}" width="{sw}" height="4" rx="2" fill="#fff" opacity=".14"/>'
          f'<rect x="{sx}" y="{sy}" width="{sw}" height="4" rx="2" fill="url(#{P}-aur)">'
          f'{A("width", [0, sw, sw, 0], kt_s, L, rep=True)}</rect>'
          f'<circle cx="{sx + sw}" cy="{sy + 2}" r="5.5" fill="#fff">'
          f'{A("cx", [sx, sx + sw, sx + sw, sx], kt_s, L, rep=True)}</circle>'
          f'<circle cx="{sx + sw}" cy="{sy + 2}" r="9" fill="{VI}" opacity=".35">'
          f'{A("cx", [sx, sx + sw, sx + sw, sx], kt_s, L, rep=True)}</circle></g>')
    for (cx, cy, r, c, dl) in [(FX + 6, FY + 70, 7, CY, 0), (FX + FW + 2, FY + 150, 9, PK, .9), (FX + FW - 30, FY + FH + 12, 6, VI, 1.6)]:
        b += sparkle(cx, cy, r, c, P, dl)

    # ------------------------------------------------------------ left column
    # open-to-collabs pill
    pw = 40 + est_w("open to collabs", 12, True)
    b += (f'<g class="{P}-in" style="animation-delay:.15s">'
          f'<rect x="{X0}" y="38" width="{pw:.0f}" height="30" rx="15" fill="#fff" fill-opacity=".04"/>'
          f'<rect x="{X0 + .5}" y="38.5" width="{pw - 1:.0f}" height="29" rx="14.5" fill="none" stroke="url(#{P}-hair)"/>'
          f'<circle cx="{X0 + 17}" cy="53" r="4" fill="{CY}"/>'
          f'<circle cx="{X0 + 17}" cy="53" r="4" fill="none" stroke="{CY}" stroke-width="1.5">'
          f'{A("r", [4, 12], [0, 1], 2, rep=True)}{A("opacity", [.8, 0], [0, 1], 2, rep=True)}</circle>'
          f'<text x="{X0 + 32}" y="57" class="{P}-jb" font-size="12" fill="{TX}">open to collabs</text></g>')

    # typed "Hi there, I'm"  (discrete steps = one character per step)
    typed = "Hi there, I'm"
    cw_, n, TT = 10.8, len("Hi there, I'm"), 2.4
    tk = [0] + [(.55 + 1.4 * (k - 1) / n) / TT for k in range(1, n + 1)]
    d += (f'<clipPath id="{P}-typeclip"><rect x="{X0}" y="92" width="{n * cw_:.1f}" height="28">'
          f'{A("width", [0] + [round(cw_ * k, 1) for k in range(1, n + 1)], tk, TT, calc="discrete")}</rect></clipPath>')
    b += (f'<text x="{X0}" y="112" class="{P}-jb" font-size="18" fill="{CY}" textLength="{n * cw_:.1f}" lengthAdjust="spacing" clip-path="url(#{P}-typeclip)">{esc(typed)}</text>'
          f'<rect x="{X0 + n * cw_ + 2:.1f}" y="97" width="9" height="18" rx="1.5" fill="{CY}">'
          f'{A("x", [X0 + 2] + [round(X0 + cw_ * k + 2, 1) for k in range(1, n + 1)], tk, TT, calc="discrete")}'
          f'<animate attributeName="opacity" values="1;0" keyTimes="0;.5" dur="1s" begin="{TT}s" repeatCount="indefinite" calcMode="discrete"/></rect>')

    # name: big animated gradient revealed by a rising mask
    name = cfg["name"]
    fs = fit(name, 470, 66)
    nb = 186
    nw = est_w(name, fs) * 1.05
    d += (f'<linearGradient id="{P}-ng" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X0 + max(nw, 240):.0f}" y2="0" spreadMethod="repeat">'
          f'<stop offset="0" stop-color="{CY}"/><stop offset=".33" stop-color="{VI}"/><stop offset=".66" stop-color="{PK}"/><stop offset="1" stop-color="{CY}"/>'
          f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{max(nw, 240):.0f} 0" dur="7s" repeatCount="indefinite"/></linearGradient>'
          f'<mask id="{P}-nm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
          f'<rect x="0" y="{nb - fs * 1.0:.1f}" width="{W}" height="{fs * 1.6:.1f}" fill="#fff">'
          f'{ENTER("y", f"{nb + fs * .45:.1f}", f"{nb - fs * 1.0:.1f}", .45, 1.15)}</rect></mask>')
    b += (f'<g mask="url(#{P}-nm)">'
          f'<text x="{X0}" y="{nb}" class="{P}-sg" font-size="{fs:.1f}" font-weight="700" fill="url(#{P}-ng)" opacity=".45" filter="url(#{P}-blur6)">{esc(name)}</text>'
          f'<text x="{X0}" y="{nb}" class="{P}-sg" font-size="{fs:.1f}" font-weight="700" fill="url(#{P}-ng)" letter-spacing="-1">{esc(name)}</text></g>')

    # cycling role lines
    roles = cfg["roles"]
    tot = 3.0 * len(roles)
    rs = ""
    for i, r in enumerate(roles):
        o, t = CYCLE(i, len(roles), tot)
        rs += (f'<g opacity="{1 if i == 0 else 0}">{o}{t}'
               f'<text x="{X0}" y="232" class="{P}-sg" font-size="{fit(r, 440, 24):.1f}" font-weight="500" fill="{TX}">'
               f'<tspan fill="{VI}">/ </tspan>{esc(r)}</text></g>')
    b += f'<g class="{P}-in" style="animation-delay:1.35s">{rs}</g>'

    # pitch
    ps = fit(cfg["pitch"], 470, 15.5)
    b += (f'<text class="{P}-in {P}-sg" style="animation-delay:1.55s" x="{X0}" y="272" font-size="{ps:.1f}" fill="{MU}">{esc(cfg["pitch"])}</text>')

    # meta row with drawn icons
    items = [("pin", cfg["city"]), ("building", cfg["company"]),
             ("star", f'{cfg["meta"]["stars"]} stars'), ("repo", f'{cfg["meta"]["repos"]} repos')]
    ms = 14.0
    gap, ic = 22, 17
    while sum(ic + 7 + est_w(t, ms) + gap for _, t in items) - gap > 480 and ms > 10:
        ms -= .5
    x = X0
    for i, (ico, t) in enumerate(items):
        b += (f'<g class="{P}-in" style="animation-delay:{1.7 + i * .12:.2f}s">'
              f'{li(ico, x, 306, ic, f"url(#{P}-aurd)", 1.9, pl=True, delay=1.7 + i * .12)}'
              f'<text x="{x + ic + 7:.0f}" y="319" class="{P}-sg" font-size="{ms}" font-weight="500" fill="{TX}">{esc(t)}</text></g>')
        x += ic + 7 + est_w(t, ms) + gap
    return svg_doc(P, W, H, b, d, "", f'{cfg["name"]} - hero',
                   f'Animated intro for {cfg["name"]}, {cfg["role"]}. Looping camera-viewfinder clip beside name, roles and links.'), dict(
        frames=N, fps=round(fps, 2), loop=L, synthetic=synthetic)

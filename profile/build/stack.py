from lib import *
import random

P = "s"
W = 900
OH = 400                      # orbit card height
CX, CY_ = 450, 200            # core centre
CORE_R, RING_R = 30, 46       # solid core / its dashed halo ring
NS = 96                       # samples per orbit lap (smooth enough at these speeds)


def rot(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def orbit_pos(o, phi):
    x, y = rot(o["rx"] * math.cos(phi), o["ry"] * math.sin(phi), o["tilt"])
    return CX + x, CY_ + y


def tile(name, r, icon, uid, glow=True):
    """glass icon tile (circle) centred on 0,0"""
    return (f'<circle r="{r}" fill="{BG}"/><circle r="{r}" fill="url(#{P}-glass)"/>'
            f'<circle r="{r - .5}" fill="none" stroke="url(#{P}-hair)" stroke-width="1.2"/>'
            f'{si(name, -icon / 2, -icon / 2, icon)}')


def build(cfg):
    d, b = "", ""
    sk = cfg["skills"]

    # ============================================================ ORBIT CARD
    b += card(P, "o", 0, 0, W, OH, 26)
    d += clip(P, "o", 0, 0, W, OH, 26)
    b += f'<g clip-path="url(#{P}-clip-o)">'
    # soft aurora wash
    b += (f'<g filter="url(#{P}-blur40)" opacity=".55"><ellipse cx="170" cy="330" rx="170" ry="80" fill="{CY}" opacity=".35"/>'
          f'<ellipse cx="730" cy="80" rx="190" ry="90" fill="{PK}" opacity=".32"/></g>')
    rnd = random.Random(7)
    for i in range(26):
        x, y, r = rnd.uniform(14, W - 14), rnd.uniform(14, OH - 14), rnd.uniform(.7, 1.6)
        b += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff" opacity=".5">'
              f'{A("opacity", [.5, .08, .5], [0, .5, 1], rnd.uniform(2.5, 5), rep=True)}</circle>')
    b += f'<text x="30" y="40" class="{P}-jb" font-size="10.5" fill="{DIM}" letter-spacing="2.5">TOOLKIT / LIVE ORBIT</text>'
    b += f'<circle cx="19" cy="36.5" r="3.5" fill="{CY}">{A("opacity", [1, .3, 1], [0, .5, 1], 2, rep=True)}</circle>'

    orbits = [
        dict(rx=198, ry=76, tilt=-22, period=22, dir=1, r=19, ic=17, phase=0.4),
        dict(rx=292, ry=112, tilt=10, period=32, dir=-1, r=19, ic=17, phase=1.0),
        dict(rx=392, ry=130, tilt=-7, period=44, dir=1, r=19, ic=17, phase=2.2),
    ]
    import numpy as np
    # per-icon starting phases: seeded hill-climb so icons stay apart, with the first 10s (= opening frame) weighted heavily
    idx_ = [(oi, j) for oi, names in enumerate(cfg["orbits"]) for j in range(len(names))]
    ts = np.concatenate([np.arange(0, 352, 1.0), np.tile(np.arange(0, 10, 0.25), 25)])
    prm = np.array([[orbits[oi]["rx"], orbits[oi]["ry"], np.radians(orbits[oi]["tilt"]), orbits[oi]["dir"], orbits[oi]["period"]] for oi, _ in idx_])
    iu = np.triu_indices(len(idx_), 1)

    def penalty(ph):
        phi = ph[:, None] + prm[:, 3:4] * 2 * np.pi * ts[None, :] / prm[:, 4:5]
        x, y = prm[:, 0:1] * np.cos(phi), prm[:, 1:2] * np.sin(phi)
        X = x * np.cos(prm[:, 2:3]) - y * np.sin(prm[:, 2:3]); Y = x * np.sin(prm[:, 2:3]) + y * np.cos(prm[:, 2:3])
        dd = np.hypot(X[:, None, :] - X[None, :, :], Y[:, None, :] - Y[None, :, :])[iu]
        return float(np.sum(np.maximum(0, 52 - dd) ** 2))
    rs = np.random.RandomState(11)
    cur = np.array([2 * np.pi * j / len(cfg["orbits"][oi]) + orbits[oi]["phase"] for oi, j in idx_]); cp = penalty(cur)
    for it in range(3500):
        cand = cur.copy(); k = rs.randint(len(cur)); cand[k] += rs.normal(0, 0.9 if it < 1500 else 0.25)
        pc = penalty(cand)
        if pc < cp:
            cur, cp = cand, pc
    PH = {ij: cur[n] for n, ij in enumerate(idx_)}
    # orbit rails (drawn first, behind everything)
    for i, o in enumerate(orbits):
        b += (f'<ellipse cx="{CX}" cy="{CY_}" rx="{o["rx"]}" ry="{o["ry"]}" transform="rotate({o["tilt"]} {CX} {CY_})" fill="none" '
              f'stroke="url(#{P}-aur)" stroke-opacity=".42" stroke-width="1.2" stroke-dasharray="2 6">'
              f'{A("stroke-dashoffset", [0, -32 * o["dir"]], [0, 1], 6 + i * 2, rep=True)}</ellipse>')

    # ---- core
    d += (f'<radialGradient id="{P}-core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{VI}" stop-opacity=".95"/>'
          f'<stop offset=".45" stop-color="{CY}" stop-opacity=".35"/><stop offset="1" stop-color="{PK}" stop-opacity="0"/></radialGradient>'
          f'<linearGradient id="{P}-coretxt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#e9d5ff"/></linearGradient>')
    b += (f'<circle cx="{CX}" cy="{CY_}" r="104" fill="url(#{P}-core)" opacity=".55">'
          f'{A("r", [92, 112, 92], [0, .5, 1], 4.5, rep=True, calc="spline", spl="0.4 0 0.6 1;0.4 0 0.6 1")}</circle>'
          f'<circle cx="{CX}" cy="{CY_}" r="{RING_R}" fill="none" stroke="{CY}" stroke-opacity=".5" stroke-dasharray="3 9" stroke-width="1.4">'
          f'<animateTransform attributeName="transform" type="rotate" values="0 {CX} {CY_};360 {CX} {CY_}" dur="24s" repeatCount="indefinite"/></circle>'
          f'<circle cx="{CX}" cy="{CY_}" r="{CORE_R}" fill="{BG}"/><circle cx="{CX}" cy="{CY_}" r="{CORE_R}" fill="url(#{P}-core)" opacity=".9"/>'
          f'<circle cx="{CX}" cy="{CY_}" r="{CORE_R - .5}" fill="none" stroke="url(#{P}-aurd)" stroke-width="1.6"/>'
          f'<text x="{CX}" y="{CY_ + 7.5}" text-anchor="middle" class="{P}-sg" font-size="22" font-weight="700" fill="url(#{P}-coretxt)">{esc(cfg["initials"])}</text>')

    # ---- orbiting icons
    host = cfg["react_host"]
    mins = []
    layers = ""
    for oi, o in enumerate(orbits):
        names = cfg["orbits"][oi]
        m = len(names)
        for j, name in enumerate(names):
            phi0 = float(PH[(oi, j)])
            pts, scs, ops = [], [], []
            for s in range(NS + 1):
                phi = phi0 + o["dir"] * 2 * math.pi * s / NS
                x, y = orbit_pos(o, phi)
                pts.append(f"{x:.1f} {y:.1f}")
                depth = (math.sin(phi) + 1) / 2
                scs.append(f"{0.84 + 0.26 * depth:.3f}")
                ops.append(f"{0.72 + 0.28 * depth:.2f}")
                if name == host:
                    mins.append(math.hypot(x - CX, y - CY_))
            is_host = name == host
            r = 25 if is_host else o["r"]
            ic = 22 if is_host else o["ic"]
            inner = f'<g>{A("transform", scs, None, o["period"], rep=True, tag="animateTransform", typ="scale")}' \
                    f'{A("opacity", ops, None, o["period"], rep=True)}{tile(name, r, ic, f"{oi}{j}")}</g>'
            moons = ""
            if is_host:
                RM = [(42, 12, 5.0, 1), (42, 12, 8.0, 0)]      # (orbit radius, moon radius, period, sweep)
                for mi, mname in enumerate(cfg["moons"][:2]):
                    rm, mr, per, sw = RM[mi]
                    path = f"M{rm} 0A{rm} {rm} 0 1 {sw} {-rm} 0A{rm} {rm} 0 1 {sw} {rm} 0Z"
                    moons += (f'<g><animateMotion dur="{per}s" repeatCount="indefinite" path="{path}" begin="0s"/>'
                              f'<g transform="translate(0 0)">{tile(mname, mr, 14, f"m{mi}")}</g></g>')
                    mins_moon = min(mins) - rm - mr
                    assert mins_moon > RING_R + 8, f"moon would crowd the core: clearance {mins_moon:.1f}px"
                # faint tether ring shows the moons' orbit
                moons = (f'<circle r="42" fill="none" stroke="{VI}" stroke-opacity=".3" stroke-dasharray="2 5"/>' + moons)
            layer = (f'<g transform="translate({pts[0]})">'
                     f'{A("transform", pts, None, o["period"], rep=True, tag="animateTransform", typ="translate")}'
                     f'{moons}{inner}</g>')
            layers += layer
    b += layers + "</g>"
    clearance = min(mins) - 42 - 12 - RING_R

    # ============================================================ CHIP GRID
    groups = list(sk.items())
    colw = (W - 56 - 16 * (len(groups) - 1)) / len(groups)
    rows = max(len(v) for _, v in groups)
    CY0 = OH + 20
    CH = 58 + rows * 40 + 18
    b += card(P, "c", 0, CY0, W, CH, 26)
    total = sum(len(v) for _, v in groups)
    cyc = total * 0.55
    idx = 0
    for gi, (gname, items) in enumerate(groups):
        x0 = 28 + gi * (colw + 16)
        b += (f'<g class="{P}-in" style="animation-delay:{.1 + gi * .12:.2f}s">'
              f'<circle cx="{x0 + 4}" cy="{CY0 + 36}" r="3.5" fill="url(#{P}-aurd)"/>'
              f'<text x="{x0 + 15}" y="{CY0 + 40}" class="{P}-jb" font-size="11" font-weight="600" fill="{MU}" letter-spacing="1.8">{esc(gname.upper())}</text></g>')
        for ci, name in enumerate(items):
            y = CY0 + 54 + ci * 40
            a = idx / total
            pk = a + .5 / total
            en = a + 1.7 / total
            if en >= 1:
                kt, vals = [0, a, min(pk, .999), 1], [0, 0, 1, 0]
            else:
                kt, vals = [0, a, pk, en, 1], [0, 0, 1, 0, 0]
            if a == 0:
                kt, vals = [0, pk, en, 1], [1, 1, 0, 0]
                kt, vals = [0, .5 / total, 1.7 / total, 1], [0.6, 1, 0, 0]
            glow = A("opacity", vals, kt, cyc, rep=True)
            b += (f'<g class="{P}-in" style="animation-delay:{.25 + idx * .04:.2f}s">'
                  f'<rect x="{x0}" y="{y}" width="{colw:.1f}" height="32" rx="10" fill="#fff" fill-opacity=".035"/>'
                  f'<rect x="{x0 + .5}" y="{y + .5}" width="{colw - 1:.1f}" height="31" rx="9.5" fill="none" stroke="#fff" stroke-opacity=".09"/>'
                  f'<rect x="{x0}" y="{y}" width="{colw:.1f}" height="32" rx="10" fill="none" stroke="url(#{P}-aurd)" stroke-width="2.4" filter="url(#{P}-blur6)" opacity="0">{glow}</rect>'
                  f'<rect x="{x0 + .5}" y="{y + .5}" width="{colw - 1:.1f}" height="31" rx="9.5" fill="none" stroke="url(#{P}-aurd)" stroke-width="1.3" opacity="0">{glow}</rect>'
                  f'{si(name, x0 + 11, y + 8, 16)}'
                  f'<text x="{x0 + 35}" y="{y + 20.5}" class="{P}-sg" font-size="13" font-weight="500" fill="{TX}">{esc(si_title(name))}</text></g>')
            idx += 1
    H = CY0 + CH
    return svg_doc(P, W, H, b, d, "", f'{cfg["name"]} - tech stack',
                   "Tech icons orbiting a glowing core on three tilted orbits, with React carrying two small moons, above a grouped grid of skill chips."), \
        dict(moon_clearance_to_core_ring_px=round(clearance, 1))

from lib import *
from PIL import Image
import hashlib, json, urllib.request

P = "b"
W, H = 900, 500
LW = 290                       # lanyard card width
DX, DW = 308, 592              # dashboard origin / width
AX, AY = 145, -6               # pendulum anchor (top of strap, just above the card)


def maybe_fetch(cfg):
    """Optional: pull live repo data. Falls back to config values on any failure."""
    if not cfg.get("fetch_repos") or cfg["username"] == "yourusername":
        return cfg
    try:
        u = cfg["username"]
        get = lambda url: json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "profile-build"}), timeout=10))
        repos = get(f"https://api.github.com/users/{u}/repos?per_page=100&type=owner")
        user = get(f"https://api.github.com/users/{u}")
        top = sorted((r for r in repos if not r["fork"]), key=lambda r: -r["stargazers_count"])[:6]
        cfg["repos"] = [{"name": r["name"], "stars": r["stargazers_count"]} for r in top]
        cfg["kpis"][0]["value"] = sum(r["stargazers_count"] for r in repos)
        cfg["kpis"][1]["value"] = user["public_repos"]
        cfg["kpis"][3]["value"] = user["followers"]
    except Exception as e:                       # network blocked / rate limited / bad user
        print("  (fetch_repos failed, using config values:", e, ")")
    return cfg


def wrap(text, n, lines=2):
    words, out, cur = text.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + (1 if cur else 0) <= n:
            cur += (" " if cur else "") + w_
        else:
            out.append(cur); cur = w_
    out.append(cur)
    return out[:lines] if len(out) <= lines else [out[0], (" ".join(out[1:]))[:n - 1] + "…"]


def odometer(cx_left, base, text, size, delay, color, p_id):
    """Count-up number built from per-digit reels (no JS). Returns (defs, body, width)."""
    LH = size * 1.25
    cell = size * 0.62
    defs, body, x = "", "", cx_left
    for i, ch in enumerate(text):
        if ch.isdigit():
            dg = int(ch)
            cid = f"{P}-reel{p_id}-{i}"
            defs += f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{base - size * .86:.1f}" width="{cell:.1f}" height="{LH * .95:.1f}"/></clipPath>'
            col = "".join(f'<text x="{x + cell / 2:.1f}" y="{base + k * LH:.1f}" text-anchor="middle" class="{P}-jb" '
                          f'font-size="{size}" font-weight="600" fill="{color}">{k % 10}</text>' for k in range(20))
            fin = -(dg + 10) * LH
            T, d0 = 14.0, delay + i * .12
            kt = [0, d0 / T, (d0 + 1.5 + i * .15) / T, 1]
            anim = A("transform", ["0 0", "0 0", f"0 {fin:.1f}", f"0 {fin:.1f}"], kt, T, rep=True, tag="animateTransform",
                     typ="translate", calc="spline", spl="0 0 1 1;0.15 0.7 0.2 1;0 0 1 1")
            body += f'<g clip-path="url(#{cid})"><g transform="translate(0 {fin:.1f})">{anim}{col}</g></g>'
            x += cell
        else:
            w_ = size * .3
            body += (f'<text x="{x + w_ / 2:.1f}" y="{base}" text-anchor="middle" class="{P}-jb" font-size="{size}" '
                     f'font-weight="600" fill="{color}">{esc(ch)}</text>')
            x += w_
    return defs, body, x - cx_left


def build(cfg):
    cfg = maybe_fetch(cfg)
    d, b = "", ""

    # ======================================================= LANYARD CARD
    b += card(P, "l", 0, 0, LW, H, 26)
    d += clip(P, "l", 0, 0, LW, H, 26)
    b += f'<g clip-path="url(#{P}-clip-l)">'
    b += (f'<g filter="url(#{P}-blur40)" opacity=".6"><circle cx="70" cy="420" r="90" fill="{CY}" opacity=".35"/>'
          f'<circle cx="230" cy="250" r="100" fill="{PK}" opacity=".3"/></g>')

    # metal + strap gradients
    d += (f'<linearGradient id="{P}-strap" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VI}" stop-opacity=".9"/>'
          f'<stop offset=".5" stop-color="{PK}" stop-opacity=".95"/><stop offset="1" stop-color="{VI}" stop-opacity=".9"/></linearGradient>'
          f'<linearGradient id="{P}-metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f8"/><stop offset=".35" stop-color="#9ea3b5"/>'
          f'<stop offset=".6" stop-color="#e6e8f0"/><stop offset="1" stop-color="#6c7186"/></linearGradient>'
          f'<linearGradient id="{P}-gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fde9a8"/><stop offset=".5" stop-color="#e0b04f"/>'
          f'<stop offset="1" stop-color="#b8802a"/></linearGradient>'
          f'<linearGradient id="{P}-foil" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
          f'<stop offset=".25" stop-color="{CY}" stop-opacity=".42"/><stop offset=".5" stop-color="{PK}" stop-opacity=".4"/>'
          f'<stop offset=".72" stop-color="#fde68a" stop-opacity=".34"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')

    # ---- swing hierarchy: drop-in > pendulum > (strap, clasp) > card lag
    A_DEG, TAU, OM = 6.0, 3.2, 2 * math.pi / 2.6
    T0, LOOP, DT = 0.95, 14.0, 0.1
    n = int(LOOP / DT)
    rot1, rot2 = [], []
    clasp_y = 172
    for i in range(n + 1):
        t = i * DT
        s = max(0.0, t - T0)
        a1 = A_DEG * math.exp(-s / TAU) * math.sin(OM * s)
        a2 = 0.5 * A_DEG * math.exp(-s / (TAU * .8)) * math.sin(1.55 * OM * s)
        rot1.append(f"{a1:.3f} {AX} {AY}")
        rot2.append(f"{a2:.3f} {AX} {clasp_y}")
    bounce = A("transform", ["0 -560", "0 0", "0 -34", "0 0", "0 -10", "0 0"], [0, .46, .64, .8, .9, 1], 1.0,
               tag="animateTransform", typ="translate", calc="spline",
               spl="0.55 0 1 0.9;0.1 0.4 0.4 1;0.55 0 1 0.9;0.1 0.4 0.4 1;0.55 0 1 0.9")
    swing = A("transform", rot1, None, LOOP, rep=True, tag="animateTransform", typ="rotate")
    lag = A("transform", rot2, None, LOOP, rep=True, tag="animateTransform", typ="rotate")

    b += f'<g>{bounce}<g>{swing}'
    # strap with printed text + stitching
    sw_ = 30
    user = cfg["username"].upper()
    span = clasp_y - 28
    printed = next((c for c in (f"{user} · OPEN TO COLLABS", f"{user} · AVAILABLE", user) if len(c) <= 26), user[:26])
    b += (f'<rect x="{AX - sw_ / 2}" y="-30" width="{sw_}" height="{clasp_y - 6 + 30}" fill="url(#{P}-strap)"/>'
          f'<rect x="{AX - sw_ / 2 + 3.5}" y="-30" width="0" height="{clasp_y + 24}" fill="none"/>'
          f'<line x1="{AX - sw_ / 2 + 3}" y1="-30" x2="{AX - sw_ / 2 + 3}" y2="{clasp_y - 6}" stroke="#fff" stroke-opacity=".4" stroke-dasharray="3 3"/>'
          f'<line x1="{AX + sw_ / 2 - 3}" y1="-30" x2="{AX + sw_ / 2 - 3}" y2="{clasp_y - 6}" stroke="#fff" stroke-opacity=".4" stroke-dasharray="3 3"/>'
          f'<text transform="translate({AX + 3.2} {clasp_y - 14}) rotate(-90)" class="{P}-jb" font-size="9" font-weight="600" letter-spacing="1.6" '
          f'fill="#fff" fill-opacity=".92" textLength="{clasp_y - 28}" lengthAdjust="spacing">{esc(printed)}</text>')
    # metal clasp: crimp plate + hook ring
    b += (f'<path d="M{AX - 17} {clasp_y - 8}h34l-3 22h-28z" fill="url(#{P}-metal)"/>'
          f'<path d="M{AX - 17} {clasp_y - 8}h34l-3 22h-28z" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width=".8"/>'
          f'<rect x="{AX - 9}" y="{clasp_y - 3}" width="18" height="5" rx="2.5" fill="#2a2d3c"/>'
          f'<ellipse cx="{AX}" cy="{clasp_y + 22}" rx="8.5" ry="11" fill="none" stroke="url(#{P}-metal)" stroke-width="4"/>')

    # ---- the badge card (secondary lag swing about the clasp)
    bx, by, bw, bh = AX - 92, 196, 184, 276
    d += (f'<clipPath id="{P}-bclip"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18"/></clipPath>'
          f'<clipPath id="{P}-pclip"><rect x="{bx + 30}" y="{by + 40}" width="124" height="136" rx="14"/></clipPath>'
          f'<linearGradient id="{P}-pbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VI}" stop-opacity=".6"/>'
          f'<stop offset="1" stop-color="{CY}" stop-opacity=".25"/></linearGradient>')
    b += f'<g>{lag}'
    b += card(P, "badge", bx, by, bw, bh, 18)
    b += (f'<rect x="{AX - 18}" y="{by + 9}" width="36" height="7" rx="3.5" fill="#05060a" stroke="#fff" stroke-opacity=".2"/>'
          f'<text x="{bx + 16}" y="{by + 36}" class="{P}-jb" font-size="9" font-weight="600" letter-spacing="2" fill="{CY}">DEV PASS</text>'
          f'<text x="{bx + bw - 16}" y="{by + 36}" text-anchor="end" class="{P}-sg" font-size="{fit(cfg["company"], 80, 11.5):.1f}" font-weight="700" fill="{TX}">{esc(cfg["company"])}</text>')
    # portrait
    src = Image.open(ROOT / "img" / "laptop_src.png")
    pw_, ph_ = src.width, round(src.width * 136 / 124)
    can = Image.new("RGBA", (pw_, ph_), (0, 0, 0, 0))
    pad = round(ph_ * .08)
    can.paste(src.crop((0, 0, pw_, ph_ - pad)), (0, pad))
    uri, _ = png_uri(can, 270, 150)
    px, py = bx + 30, by + 40
    b += (f'<rect x="{px}" y="{py}" width="124" height="136" rx="14" fill="url(#{P}-pbg)"/>'
          f'<rect x="{px}" y="{py}" width="124" height="136" rx="14" fill="url(#{P}-dots)" opacity=".9"/>'
          f'<g clip-path="url(#{P}-pclip)"><image x="{px}" y="{py + 4}" width="124" height="136" xlink:href="{uri}"/></g>'
          f'<rect x="{px}" y="{py}" width="124" height="136" rx="14" fill="none" stroke="#fff" stroke-opacity=".18"/>'
          # light travelling around the frame
          f'<rect x="{px}" y="{py}" width="124" height="136" rx="14" fill="none" stroke="url(#{P}-aurd)" stroke-width="3" stroke-linecap="round" '
          f'pathLength="1" stroke-dasharray=".16 .84" stroke-dashoffset="0" filter="url(#{P}-blur6)">{A("stroke-dashoffset", [0, -1], [0, 1], 3.4, rep=True)}</rect>'
          f'<rect x="{px}" y="{py}" width="124" height="136" rx="14" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" '
          f'pathLength="1" stroke-dasharray=".1 .9" stroke-dashoffset="0">{A("stroke-dashoffset", [0, -1], [0, 1], 3.4, rep=True)}</rect>')
    # identity
    b += (f'<text x="{AX}" y="{by + 198}" text-anchor="middle" class="{P}-sg" font-size="{fit(cfg["name"], 150, 18):.1f}" font-weight="700" fill="{TX}">{esc(cfg["name"])}</text>'
          f'<text x="{AX}" y="{by + 215}" text-anchor="middle" class="{P}-sg" font-size="{fit(cfg["role"], 152, 11.5):.1f}" font-weight="500" fill="{MU}">{esc(cfg["role"])}</text>'
          f'<line x1="{bx + 16}" y1="{by + 227}" x2="{bx + bw - 16}" y2="{by + 227}" stroke="#fff" stroke-opacity=".12" stroke-dasharray="2 4"/>')
    # gold chip
    cx0, cy0 = bx + 16, by + 238
    b += (f'<rect x="{cx0}" y="{cy0}" width="34" height="26" rx="5" fill="url(#{P}-gold)"/>'
          f'<path d="M{cx0 + 11} {cy0}v26M{cx0 + 23} {cy0}v26M{cx0} {cy0 + 9}h34M{cx0} {cy0 + 17}h34" stroke="#7a5412" stroke-opacity=".55" stroke-width=".9" fill="none"/>'
          f'<rect x="{cx0 + 11}" y="{cy0 + 9}" width="12" height="8" rx="2" fill="none" stroke="#7a5412" stroke-opacity=".7"/>')
    # barcode from a hash of the username
    h_ = hashlib.sha1(cfg["username"].encode()).digest()
    x, k = bx + 62, 0
    bars = ""
    while x < bx + bw - 16:
        wbar = 1 + (h_[k % 20] >> (k % 5)) % 3 * .8
        if x + wbar > bx + bw - 16:
            break
        bars += f'<rect x="{x:.1f}" y="{cy0}" width="{wbar:.1f}" height="26" fill="#e8eaf6" fill-opacity=".85"/>'
        x += wbar + 1.1 + (h_[(k + 7) % 20] % 2) * .9
        k += 1
    b += bars + f'<text x="{bx + bw - 16}" y="{by + 273}" text-anchor="end" class="{P}-jb" font-size="7.5" letter-spacing="1.6" fill="{DIM}">ID-{h_[:3].hex().upper()}</text>'
    # holographic foil sweep (clipped to the badge)
    foil = A("transform", ["-150 0", "330 0", "330 0"], [0, .42, 1], 6.5, rep=True, tag="animateTransform", typ="translate")
    b += (f'<g clip-path="url(#{P}-bclip)"><g transform="translate(330 0)">{foil}'
          f'<g transform="rotate(18 {bx} {by + 130})"><rect x="{bx - 40}" y="{by - 60}" width="54" height="{bh + 120}" fill="url(#{P}-foil)"/></g></g></g>')
    b += "</g></g></g></g>"   # lag, swing, drop, clip

    # ======================================================= DASHBOARD
    # --- KPI tiles
    kw = (DW - 36) / 4
    icons = ["star", "repo", "activity", "users"]
    for i, k_ in enumerate(cfg["kpis"][:4]):
        x = DX + i * (kw + 12)
        b += card(P, f"k{i}", x, 0, kw, 96, 20)
        txt = f"{k_['value']:,}"
        dd, bd, _ = odometer(x + 18, 70, txt, 31, .5 + i * .12, TX, i)
        d += dd
        b += (f'<g class="{P}-in" style="animation-delay:{.15 + i * .1:.2f}s">'
              f'<text x="{x + 18}" y="28" class="{P}-jb" font-size="10" fill="{MU}" letter-spacing="1.6">{esc(k_["label"].upper())}</text>'
              f'{li(icons[i], x + kw - 34, 15, 16, f"url(#{P}-aurd)", 2)}{bd}</g>')
    # --- bar chart
    cy0, ch = 108, H - 108
    cw = 362
    b += card(P, "chart", DX, cy0, cw, ch, 22)
    b += (f'<text x="{DX + 22}" y="{cy0 + 36}" class="{P}-sg" font-size="16" font-weight="700" fill="{TX}">Most-starred repos</text>'
          f'<text x="{DX + 22}" y="{cy0 + 54}" class="{P}-jb" font-size="10" fill="{DIM}" letter-spacing="1.2">STARS · ALL TIME</text>')
    repos = cfg["repos"][:6]
    mx = max(r["stars"] for r in repos)
    tw = cw - 44 - 50
    d += (f'<linearGradient id="{P}-bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7c5cf0"/><stop offset="1" stop-color="#b9a4ff"/></linearGradient>')
    top = cy0 + 78
    step = (ch - 78 - 20) / len(repos)
    for gx in (0, .5, 1):
        b += f'<line x1="{DX + 22 + tw * gx:.1f}" y1="{top - 8}" x2="{DX + 22 + tw * gx:.1f}" y2="{top + step * len(repos) - 14}" stroke="#fff" stroke-opacity=".06"/>'
    for i, r_ in enumerate(repos):
        y = top + i * step
        bw_ = max(8, tw * r_["stars"] / mx)
        dl = .55 + i * .13
        b += (f'<g class="{P}-in" style="animation-delay:{dl - .2:.2f}s"><text x="{DX + 22}" y="{y + 10}" class="{P}-sg" font-size="12.5" font-weight="500" fill="{TX}">{esc(r_["name"])}</text></g>'
              f'<rect x="{DX + 22}" y="{y + 18}" width="{tw:.1f}" height="10" rx="5" fill="#fff" fill-opacity=".05"/>'
              f'<rect x="{DX + 22}" y="{y + 18}" width="{bw_:.1f}" height="10" rx="5" fill="url(#{P}-bar)">{ENTER("width", 0, f"{bw_:.1f}", dl, 1.0)}</rect>'
              f'<text x="{DX + 22 + bw_ + 8:.1f}" y="{y + 27}" class="{P}-jb" font-size="11" font-weight="600" fill="#c4b5fd">'
              f'{ENTER("x", f"{DX + 30:.1f}", f"{DX + 22 + bw_ + 8:.1f}", dl, 1.0)}{ENTER("opacity", 0, 1, dl, .6)}{r_["stars"]:,}</text>')
    # --- now panel
    nx, nw = DX + cw + 12, DW - cw - 12
    b += card(P, "now", nx, cy0, nw, ch, 22)
    b += (f'<circle cx="{nx + 24}" cy="{cy0 + 34}" r="4" fill="{PK}"/>'
          f'<circle cx="{nx + 24}" cy="{cy0 + 34}" r="4" fill="none" stroke="{PK}" stroke-width="1.4">{A("r", [4, 11], [0, 1], 1.8, rep=True)}{A("opacity", [.9, 0], [0, 1], 1.8, rep=True)}</circle>'
          f'<text x="{nx + 38}" y="{cy0 + 38}" class="{P}-jb" font-size="11" font-weight="600" letter-spacing="3" fill="{TX}">NOW</text>')
    nicons = ["rocket", "cpu", "book", "headphones"]
    per = (ch - 70) / 4
    for i, it in enumerate(cfg["now"][:4]):
        y = cy0 + 64 + i * per
        lines = wrap(it["value"], 19)
        b += (f'<g class="{P}-in" style="animation-delay:{.7 + i * .14:.2f}s">'
              f'<rect x="{nx + 18}" y="{y}" width="34" height="34" rx="10" fill="url(#{P}-aurd)" fill-opacity=".14"/>'
              f'<rect x="{nx + 18.5}" y="{y + .5}" width="33" height="33" rx="9.5" fill="none" stroke="url(#{P}-hair)"/>'
              f'{li(nicons[i], nx + 27, y + 9, 16, f"url(#{P}-aurd)", 2)}'
              f'<text x="{nx + 62}" y="{y + 11}" class="{P}-jb" font-size="9.5" fill="{MU}" letter-spacing="1.5">{esc(it["label"].upper())}</text>'
              + "".join(f'<text x="{nx + 62}" y="{y + 28 + j * 16}" class="{P}-sg" font-size="13" font-weight="500" fill="{TX}">{esc(ln)}</text>' for j, ln in enumerate(lines))
              + '</g>')
    return svg_doc(P, W, H, b, d, "", f'{cfg["name"]} - ID badge & dashboard',
                   "A lanyard ID badge swinging on a strap beside GitHub KPIs, a most-starred repos chart and a now panel."), dict(
        pendulum=f"A={A_DEG}deg tau={TAU}s T={2.6}s")

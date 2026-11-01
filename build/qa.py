#!/usr/bin/env python3
"""Render each SVG in headless Chromium at several timestamps and run static checks.
   python3 qa.py hero.svg 0 0.6 1.5 3.4   -> shots in /home/claude/profile/build/qa/
   python3 qa.py --static hero.svg        -> renders with ALL animation stripped (finished-state check)"""
import sys, re, pathlib
from playwright.sync_api import sync_playwright
from lib import ROOT
ASSETS = ROOT.parent / "assets"; QA = ROOT / "qa"; QA.mkdir(exist_ok=True)

def strip_anim(svg):
    svg = re.sub(r"<(animate|animateTransform|animateMotion|set)\b[^>]*?(/>|>.*?</\1>)", "", svg, flags=re.S)
    svg = re.sub(r"animation:[^;}]*;?", "", svg)
    return svg

def shot(name, times, static=False):
    f = ASSETS / name; svg = f.read_text()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(device_scale_factor=1.5)
        w = int(re.search(r'width="(\d+)"', svg).group(1)); h = int(re.search(r'height="(\d+)"', svg).group(1))
        pg.set_viewport_size({"width": w, "height": h})
        reqs = []; pg.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:", "data:")) else None)
        if static:
            tmp = QA / ("_static_" + name); tmp.write_text(strip_anim(svg)); pg.goto("file://" + str(tmp))
            pg.wait_for_timeout(300); pg.screenshot(path=str(QA / f"{name[:-4]}_static.png")); print("static ->", name)
        else:
            pg.goto("file://" + str(f)); pg.wait_for_timeout(300)
            for t in times:
                pg.evaluate("""(t)=>{const s=document.documentElement; s.pauseAnimations(); s.setCurrentTime(t);
                   document.getAnimations().forEach(a=>{a.pause(); a.currentTime=t*1000;});}""", t)
                pg.wait_for_timeout(120)
                out = QA / f"{name[:-4]}_t{str(t).replace('.', '_')}.png"; pg.screenshot(path=str(out)); print("shot", out.name)
        if reqs: print("!! NETWORK REQUESTS:", reqs)
        b.close()

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--static": shot(a[1], [], True)
    else: shot(a[0], [float(x) for x in a[1:]] or [0, 1, 3])

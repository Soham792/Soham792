#!/usr/bin/env python3
"""Generate every SVG + README.  Usage:  python3 build.py [hero about stack badge connect readme]"""
import sys, pathlib, importlib, json
from lib import load_cfg, ROOT

OUT = ROOT.parent / "assets"
MODS = {"hero": "hero", "about": "about", "stack": "stack", "badge": "badge", "connect": "connect"}
FILES = {"hero": "hero.svg", "about": "about-life.svg", "stack": "stack.svg", "badge": "id-dashboard.svg", "connect": "connect.svg"}

def main(which):
    cfg = load_cfg(); OUT.mkdir(exist_ok=True)
    for k in which:
        if k == "readme": continue
        m = importlib.import_module(MODS[k])
        res = m.build(cfg)
        svg, info = res if isinstance(res, tuple) else (res, {})
        p = OUT / FILES[k]; p.write_text(svg, encoding="utf-8")
        print(f"{FILES[k]:18s} {len(svg)/1024:8.1f} KB  {info if info else ''}")
    if "readme" in which or len(which) == len(MODS):
        import readme; readme.write(cfg)

if __name__ == "__main__":
    main(sys.argv[1:] or [*MODS, "readme"])

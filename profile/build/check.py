#!/usr/bin/env python3
"""Static compliance checks for the generated files (no browser needed)."""
import re, glob, os, collections, xml.dom.minidom as m
from lib import ROOT
A = ROOT.parent
PREF = {'hero.svg': 'h', 'about-life.svg': 'a', 'stack.svg': 's', 'id-dashboard.svg': 'b', 'connect.svg': 'c'}
ok = True
for n, pref in PREF.items():
    s = (A / 'assets' / n).read_text(); issues = []
    try: m.parseString(s)
    except Exception as e: issues.append('XML ' + str(e))
    if re.search(r'<script|onload=|onclick=', s): issues.append('script/handler')
    ext = [h for h in re.findall(r'href="([^"]+)"', s) if not h.startswith(('data:image/png', 'data:image/jpeg', '#'))]
    if ext: issues.append(f'external href {ext[:2]}')
    if re.search(r'url\(\s*["\']?https?:|@import', s): issues.append('external url()/@import')
    if 'webp' in s.lower(): issues.append('webp')
    ids = re.findall(r' id="([^"]+)"', s)
    if [k for k, v in collections.Counter(ids).items() if v > 1]: issues.append('duplicate ids')
    if [i for i in ids if not i.startswith(pref + '-')]: issues.append('un-namespaced ids')
    if s.count('font/woff2;base64') != 4: issues.append('fonts not embedded')
    size = os.path.getsize(A / 'assets' / n)
    if size > 4_500_000: issues.append('over 4.5MB (GitHub proxy limit ~5MB)')
    print(f'{n:18s}{size / 1024:7.0f} KB  SMIL={len(re.findall("<animate", s)):3d}  ', 'OK' if not issues else issues); ok &= not issues
r = (A / 'README.md').read_text(); imgs = re.findall(r'<img src="([^"]+)"', r)
good = all(i.endswith('?v=1') for i in imgs); print(f'README: {len(imgs)} images, all cache-busted: {good}'); ok &= good
print('ALL CHECKS PASS' if ok else 'CHECKS FAILED')

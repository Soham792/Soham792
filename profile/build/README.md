# Build the profile

```bash
pip install pillow numpy scipy fonttools brotli playwright   # playwright only for qa.py
python3 build.py            # regenerates ../assets/*.svg, ../README.md, ../.github/workflows/profile-3d.yml
python3 qa.py hero.svg 0.5 1.5 3.4      # screenshots at those seconds  -> build/qa/
python3 qa.py --static hero.svg          # render with ALL animation stripped (finished-state check)
```

* **Everything personal lives in `config.json`** (name, role, username, email, city, company, skills, hobbies, KPIs, repos, links, projects).
* **Video:** drop your clip at `build/clip.mp4` and rebuild. Frames are extracted with ffmpeg (fps is lowered automatically so the SVG stays under `max_frames`; tune in `config.json -> clip`). Without a clip, `hero.svg` uses a stand-in push-in made from your portrait.
* **Live repo numbers:** set `"fetch_repos": true` (and a real username) to pull stars/repos/followers from the GitHub API at build time.
* Add more Simple Icons: `npm i simple-icons si13@npm:simple-icons@13.21.0`, edit `WANT` in `extract_icons.js`, run `node extract_icons.js` (si13 supplies LinkedIn/OpenAI/D3, removed from newer releases).
* After pushing a visual change, bump `?v=1` -> `?v=2` in `readme.py` (GitHub's image proxy caches aggressively).

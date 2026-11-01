"""Frame source for hero.svg.
 * If build/clip.mp4 exists: ffmpeg extracts its frames (fps capped so the SVG stays small).
 * Otherwise: a stand-in clip (slow push-in + light sweep) is synthesised from your portrait,
   so the whole pipeline works today; drop in clip.mp4 and rebuild to use the real video."""
import io, subprocess, tempfile, pathlib, json
import numpy as np
from PIL import Image
from lib import ROOT, BG

def _hex(c): return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))

def from_video(path, W, H, fps, max_frames):
    dur = float(json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)]))["format"]["duration"])
    fps = min(fps, max_frames / dur)
    with tempfile.TemporaryDirectory() as t:
        subprocess.check_call(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
            f"fps={fps:.4f},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
            "-q:v", "5", f"{t}/f%03d.jpg"])
        files = sorted(pathlib.Path(t).glob("f*.jpg"))
        return [f.read_bytes() for f in files], fps, False

def synthesize(W, H, fps, n=22):
    src = Image.open(ROOT / "img" / "laptop_src.png").convert("RGBA")
    flat = Image.new("RGBA", src.size, _hex(BG) + (255,)); flat.alpha_composite(src)
    flat = flat.convert("RGB")
    cw = src.width; ch = round(cw * H / W)                      # crop from the top: head + torso + laptop
    pad = round(ch * 0.11)                                       # headroom above the sunglasses
    base = Image.new("RGB", (cw, ch), _hex(BG)); base.paste(flat.crop((0, 0, cw, ch - pad)), (0, pad))
    out = []
    yy, xx = np.mgrid[0:H, 0:W]
    for i in range(n):
        e = i / (n - 1); e = e * e * (3 - 2 * e)                  # smoothstep
        z = 1.0 + 0.075 * e
        bw, bh = cw / z, base.height / z
        fx, fy = 0.5 * cw, 0.34 * base.height                     # keep the face anchored while we push in
        x0 = fx - (fx / cw) * bw; y0 = fy - (fy / base.height) * bh
        fr = base.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
        a = np.asarray(fr).astype(np.float32)
        d = (xx / W * 0.8 + yy / H * 0.6) - (e * 2.0 - 0.5)       # diagonal light sweep, left -> right
        band = np.exp(-(d * 7.0) ** 2)[..., None] * np.array([34, 211, 238], np.float32) * 0.17
        a = np.clip(a + band, 0, 255).astype(np.uint8)
        buf = io.BytesIO(); Image.fromarray(a).save(buf, "JPEG", quality=76, optimize=True); out.append(buf.getvalue())
    return out, fps, True

def get_frames(cfg, W, H):
    c = cfg["clip"]; p = ROOT / c["file"]
    if p.exists():
        return from_video(p, W, H, c["fps"], c["max_frames"])
    return synthesize(W, H, c["fps"])

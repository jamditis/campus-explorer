"""Film finish for the teaser frames: grade, letterbox, vignette, bloom and grain, then encode.

    python3 tools/teaser/finish.py OUT_DIR [--fps 30] [--from F] [--to F] [--no-encode]

Reads OUT_DIR/frames/NNNNN.png (raw captures) and OUT_DIR/plan.json (written by capture.mjs: per
frame the shot's grade and how far the film look is on, 0 for the interface bookends), writes
OUT_DIR/graded/NNNNN.png and encodes OUT_DIR/teaser.mp4 (H.264, yuv420p, faststart, no sound).
A missing raw frame repeats the one before it (so an animatic shot with --step can be cut too).
Everything is done on the rendered pixels: nothing is added to the picture but the grade and grain.
"""

import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

ASPECT = 2.39  # film frame inside the 16:9 picture when the film look is fully on


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def grade(img, g, k, n):
    """img: float RGB 0..1; g: grade settings; k: how far the film look is on (0..1); n: frame."""
    if k <= 0:
        return img
    h, w, _ = img.shape
    out = img.copy()
    # bloom: soft glow from the brightest parts (sky near the sun, lamps)
    if g.get("bloom", 0.25) > 0:
        lum = out.mean(axis=2)
        hi = np.clip((lum - 0.72) / 0.28, 0, 1)[..., None] * out
        small = Image.fromarray((hi * 255).astype(np.uint8))
        small = small.resize((w // 4, h // 4), Image.BILINEAR)
        glow = small.filter(ImageFilter.GaussianBlur(6)).resize((w, h), Image.BILINEAR)
        out = out + np.asarray(glow, dtype=np.float32) / 255 * g.get("bloom", 0.25)
    # white balance and lift / gamma / gain, per channel
    warm = g.get("warm", 0.0)  # + warmer, - cooler
    gain = np.array([1 + 0.06 * warm, 1.0, 1 - 0.08 * warm], dtype=np.float32) * g.get("gain", 1.0)
    lift = np.array(g.get("lift", [0.0, 0.0, 0.0]), dtype=np.float32)
    out = np.clip(out * gain, 0, None)
    out = lift + out * (1 - lift)
    out = np.clip(out, 0, 1) ** (1 / g.get("gamma", 1.0))
    # gentle S-curve around mid grey
    c = g.get("contrast", 0.12)
    out = out + c * (out - 0.5) * (1 - np.abs(2 * out - 1))
    # saturation
    s = g.get("sat", 1.0)
    grey = out.mean(axis=2, keepdims=True)
    out = grey + (out - grey) * s
    # vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / np.sqrt(2)
    out = out * (1 - g.get("vignette", 0.22) * smooth((r - 0.45) / 0.55)[..., None])
    # grain: fine, luminance only, seeded per frame so it moves
    rng = np.random.default_rng(n)
    grain = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
    grain = np.asarray(Image.fromarray(grain).resize((w, h), Image.BILINEAR))
    out = out + grain[..., None] * g.get("grain", 0.018)
    out = np.clip(out, 0, 1)
    return img + (out - img) * k


def letterbox(img, k):
    """Black bars eased in by k toward a 2.39:1 frame."""
    if k <= 0:
        return img
    h, w, _ = img.shape
    bar = (h - w / ASPECT) / 2 * float(smooth(k))
    b = int(round(bar))
    if b > 0:
        img[:b] = 0
        img[h - b:] = 0
    return img


def main(out, fps=30, start=0, end=None, encode=True):
    plan = json.load(open(os.path.join(out, "plan.json")))
    raw, dst = os.path.join(out, "frames"), os.path.join(out, "graded")
    os.makedirs(dst, exist_ok=True)
    end = len(plan["frames"]) if end is None else end
    last = None
    for n in range(start, end):
        p = plan["frames"][n]
        src = os.path.join(raw, f"{n:05d}.png")
        if os.path.exists(src):
            last = src
        if last is None:
            continue
        target = os.path.join(dst, f"{n:05d}.png")
        if os.path.exists(target) and os.path.getmtime(target) > os.path.getmtime(last):
            continue
        img = np.asarray(Image.open(last).convert("RGB"), dtype=np.float32) / 255
        img = grade(img, plan["grades"][p["grade"]], p["film"], n)
        img = letterbox(img, p["bars"])
        Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(target, compress_level=1)
    if encode:
        mp4 = os.path.join(out, "teaser.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
            "-i", os.path.join(dst, "%05d.png"), "-c:v", "libx264", "-preset", "slow", "-crf", "17",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4,
        ], check=True)
        print(mp4)


if __name__ == "__main__":
    a = sys.argv[1:]

    def opt(name, d):
        return type(d)(a[a.index(name) + 1]) if name in a else d

    main(a[0], opt("--fps", 30), opt("--from", 0), opt("--to", -1) if "--to" in a else None,
         "--no-encode" not in a)

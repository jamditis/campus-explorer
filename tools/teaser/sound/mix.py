"""Build the teaser soundtrack from recorded sources, a cue sheet and the film's shot list.

    python3 tools/teaser/sound/mix.py SRC_DIR OUT_DIR [--timeline FILE] [--cues FILE]
                                      [--video FILM.mp4] [--lufs -16] [--tp -1.5]

SRC_DIR holds the downloaded recordings, named by their key in `cues.json` (`sources`), any audio
format ffmpeg reads. The shot list comes from `--timeline` (JSON written by `timeline.mjs` from the
film's storyboard), else from `shots.default.json`. Cues are placed by shot name and an offset, by a
3D graphic's id (`in`, `land`, `out`), or by a storyboard marker, so a re-timed cut needs no new cue
times. Writes OUT_DIR/teaser_mix.wav (48 kHz, 24-bit, stereo), teaser_mix.m4a (AAC), stems per bus,
report.json (loudness, true peak, clipping) and, with --video, teaser_with_sound.mp4 (video copied).

Every sound is a recording; this script only cuts, filters, fades, pans and sums them.
"""

import json
import os
import subprocess
import sys

import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
BUSES = ("amb", "place", "music", "fx", "ui")
MASTER_NOTES = {}  # what the master stage did, for report.json


# ---------------------------------------------------------------- pure helpers (unit tested)


def shot_table(timeline, names=None):
    """{role: (start, end)} in seconds. `names` maps cue-sheet roles to storyboard shot names."""
    by_name = {s["name"]: (s["start"], s["start"] + s["duration"]) for s in timeline["shots"]}
    out = dict(by_name)
    for role, name in (names or {}).items():
        if name in by_name:
            out[role] = by_name[name]
    return out


def graphic_table(timeline):
    """{graphic id: {in, land, out}} in film seconds. `land` is when the eased rise has settled."""
    out = {}
    for s in timeline["shots"]:
        for g in s.get("graphics", []):
            if g["id"] in out or g.get("in", 0.0) < 0:  # carried over from an earlier shot
                continue
            t_in = s["start"] + g.get("in", 0.0)
            dur = g.get("inDur", 0.6)
            end = g.get("out")
            out[g["id"]] = {
                "in": t_in,
                "land": t_in + 0.85 * dur,
                "out": s["start"] + end if end is not None else s["start"] + s["duration"],
            }
    return out


def resolve(anchor, shots, graphics=None, markers=None):
    """Film time in seconds of an anchor.

    [role, 2.0] 2 s into the shot; [role, "end-1.5"] 1.5 s before its end; [role, "50%"] halfway;
    {"graphic": id, "edge": "land", "offset": -0.3}; {"marker": name, "offset": 0};
    {"any": [anchor, ...]} the first that exists; a bare number is already film time.
    Unknown names raise KeyError so a renamed shot fails loudly.
    """
    if isinstance(anchor, int | float):
        return float(anchor)
    if isinstance(anchor, dict):
        off = float(anchor.get("offset", 0.0))
        if "any" in anchor:  # the first alternative that exists in this cut
            for a in anchor["any"]:
                try:
                    return resolve(a, shots, graphics, markers) + off
                except (KeyError, TypeError):
                    continue
            raise KeyError(f"no alternative of {anchor} in this cut")
        if "graphic" in anchor:
            return (graphics or {})[anchor["graphic"]][anchor.get("edge", "in")] + off
        if "marker" in anchor:
            return float((markers or {})[anchor["marker"]]) + off
        if "shot" in anchor:
            return resolve([anchor["shot"], anchor.get("at", 0.0)], shots) + off
        raise KeyError(f"bad anchor {anchor}")
    role, at = anchor
    start, end = shots[role]
    if isinstance(at, str):
        if at == "end":
            return end
        if at.startswith("end"):
            return end + float(at[3:])
        if at.endswith("%"):
            return start + (end - start) * float(at[:-1]) / 100
        return start + float(at)
    return start + float(at)


def fade_curve(n, kind="in"):
    """Equal-power fade of n samples (sin/cos quarter wave): no dip when two fades cross."""
    if n <= 0:
        return np.ones(0, dtype=np.float32)
    x = (np.arange(n, dtype=np.float64) + 0.5) / n
    c = np.sin(x * np.pi / 2) if kind == "in" else np.cos(x * np.pi / 2)
    return c.astype(np.float32)


def pan_gains(pan):
    """Constant-power gains (left, right) for pan in [-1, 1]."""
    th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return float(np.cos(th)), float(np.sin(th))


def envelope(times, points, n, rate=SR):
    """Gain (linear) over n samples from [[t, dB], ...] breakpoints (t in seconds from the cue
    start), interpolated in dB, held flat outside."""
    if not points:
        return np.ones(n, dtype=np.float32)
    ts = np.array([p[0] for p in points], dtype=np.float64)
    ds = np.array([p[1] for p in points], dtype=np.float64)
    t = np.arange(n, dtype=np.float64) / rate if times is None else times
    return (10 ** (np.interp(t, ts, ds) / 20)).astype(np.float32)


def duck_gain(side, depth_db, rate=SR, block=0.01, attack=0.02, release=0.35, floor=1e-4):
    """Gain curve that dips by up to depth_db while `side` (mono key signal, 0..1 scale) is loud.

    Block RMS of the key, normalised by its own peak block, drives a smoothed dip with separate
    attack and release times. Returns a linear gain per sample (1 where the key is silent).
    """
    n = len(side)
    b = max(1, int(rate * block))
    m = (n + b - 1) // b
    pad = np.zeros(m * b, dtype=np.float32)
    pad[:n] = side
    rms = np.sqrt((pad.reshape(m, b) ** 2).mean(1))
    peak = rms.max()
    if peak < floor:
        return np.ones(n, dtype=np.float32)
    key = np.clip(rms / peak, 0, 1)
    ka, kr = np.exp(-block / attack), np.exp(-block / release)
    sm = np.zeros(m)
    v = 0.0
    for i, k in enumerate(key):
        c = ka if k > v else kr
        v = c * v + (1 - c) * k
        sm[i] = v
    g = 10 ** (-depth_db * sm / 20)
    return np.repeat(g, b)[:n].astype(np.float32)


# ---------------------------------------------------------------- audio I/O through ffmpeg


def source_path(src_dir, name):
    p = os.path.join(src_dir, name)
    if os.path.exists(p):
        return p
    stem = os.path.splitext(name)[0]
    for f in sorted(os.listdir(src_dir)):
        if os.path.splitext(f)[0] == stem:
            return os.path.join(src_dir, f)
    raise FileNotFoundError(f"{name} not in {src_dir}")


def ffmpeg_filters(c):
    """ffmpeg audio filter chain for one cue (applied before fades and envelopes)."""
    f = []
    if c.get("rev"):
        f.append("areverse")
    rate = c.get("rate", 1.0)
    if rate != 1.0:
        f.append(f"asetrate={SR * rate:.3f},aresample={SR}")
    if c.get("hp"):
        f.append(f"highpass=f={c['hp']}:poles=2")
    if c.get("lp"):
        f.append(f"lowpass=f={c['lp']}:poles=2")
    for freq, gain, q in c.get("eq", []):
        f.append(f"equalizer=f={freq}:t=q:w={q}:g={gain}")
    return f


def decode(path, start, dur, filters, channels=None):
    """(samples, channels) float32 at 48 kHz: `dur` seconds of output from `start` in the file."""
    rate = 1.0
    for x in filters:
        if x.startswith("asetrate="):
            rate = float(x.split("=")[1].split(",")[0]) / SR
    pre = []
    if filters and filters[0] == "areverse":
        # reverse the needed span only: trim first, then reverse
        pre = [f"atrim=start={start}:duration={dur * rate + 0.05}", "asetpts=PTS-STARTPTS"]
        start = 0
    chain = ",".join([f"aresample={SR}"] + pre + filters)
    cmd = ["ffmpeg", "-v", "error", "-nostdin"]
    if start:
        cmd += ["-ss", f"{start:.4f}"]
    if not pre:
        cmd += ["-t", f"{dur * rate + 0.05:.4f}"]
    cmd += ["-i", path, "-af", chain, "-f", "f32le", "-ac", str(channels or 2), "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, channels or 2)
    n = int(round(dur * SR))
    if len(x) < n:
        x = np.vstack([x, np.zeros((n - len(x), x.shape[1]), np.float32)])
    return x[:n].copy()


def channels_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=channels", "-of", "csv=p=0", path],
                         capture_output=True, text=True)
    return int(out.stdout.strip() or 2)


def render_cue(c, src_dir, sources, t0, t1, shots, graphics, markers):
    """The cue as stereo samples from t0 to t1 (film seconds)."""
    path = source_path(src_dir, sources[c["key"]])
    dur = t1 - t0
    n = int(round(dur * SR))
    mono = c.get("mono") or channels_of(path) == 1
    x = decode(path, c.get("src", 0.0), dur, ffmpeg_filters(c), 1 if mono else 2)[:n]
    if mono:
        gl, gr = pan_gains(c.get("pan", 0.0))
        x = np.hstack([x * gl, x * gr]) * np.sqrt(2)  # centre = unity on each side
    else:
        w = c.get("width", 1.0)
        if w != 1.0:
            mid, side = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2 * w
            x = np.stack([mid + side, mid - side], 1)
        bal = c.get("pan", 0.0)
        if bal:
            x = x * np.array([min(1, 1 - bal), min(1, 1 + bal)], np.float32)
    g = np.full(n, 10 ** (c.get("gain", 0.0) / 20), np.float32)
    pts = []
    for t, db in c.get("env", []):
        tt = t if isinstance(t, int | float) else resolve(t, shots, graphics, markers) - t0
        pts.append([tt, db])
    if pts:
        g *= envelope(None, sorted(pts), n)
    fi, fo = int(c.get("fade_in", 0.01) * SR), int(c.get("fade_out", 0.01) * SR)
    fi, fo = min(fi, n // 2), min(fo, n // 2)
    g[:fi] *= fade_curve(fi, "in")
    if fo:
        g[n - fo:] *= fade_curve(fo, "out")
    return x * g[:, None]


# ---------------------------------------------------------------- mix


def build(cue_sheet, timeline, src_dir):
    names = cue_sheet.get("shots", {})
    shots = shot_table(timeline, names)
    graphics = graphic_table(timeline)
    for mine, theirs in cue_sheet.get("graphics", {}).items():
        if theirs in graphics:
            graphics[mine] = graphics[theirs]
    markers = dict(timeline.get("markers", {}))
    for mine, theirs in cue_sheet.get("markers", {}).items():
        if theirs in markers:
            markers[mine] = markers[theirs]
    for name, anchor in cue_sheet.get("marker_fallback", {}).items():
        if name not in markers:
            markers[name] = resolve(anchor, shots, graphics, markers)
    total = timeline["total"] + cue_sheet.get("tail", 0.0)
    n = int(round(total * SR))
    bus = {b: np.zeros((n, 2), np.float32) for b in BUSES}
    key = np.zeros(n, np.float32)  # what the beds duck under
    duck_depth = 0.0
    placed = []
    for c in cue_sheet["cues"]:
        if c.get("off"):
            continue
        t0 = resolve(c["at"], shots, graphics, markers) + c.get("shift", 0.0)
        if "until" in c:
            t1 = resolve(c["until"], shots, graphics, markers) + c.get("until_shift", 0.0)
        else:
            t1 = t0 + c["dur"]
        t0, t1 = max(0.0, t0), min(total, t1)
        if "align" in c:  # a moment in the source lands on an anchor: {"src": 38.0, "to": anchor}
            at = resolve(c["align"]["to"], shots, graphics, markers)
            c = dict(c, src=c["align"]["src"] - (at - t0))
            if c["src"] < 0:  # the source starts later than the cue: wait for it
                t0 -= c["src"]
                c["src"] = 0.0
            later = [p for p in c["align"].get("snap", []) if p >= c["src"]]
            if later:  # enter on the next phrase of the recording, not mid-phrase
                t0 += later[0] - c["src"]
                c["src"] = later[0]
        if t1 - t0 < 0.005:
            continue
        x = render_cue(c, src_dir, cue_sheet["sources"], t0, t1, shots, graphics, markers)
        a = int(round(t0 * SR))
        x = x[: n - a]
        bus[c.get("bus", "fx")][a:a + len(x)] += x
        if c.get("duck"):
            key[a:a + len(x)] += np.abs(x).mean(1) * 10 ** (c["duck"] / 20)
            duck_depth = max(duck_depth, cue_sheet.get("duck_db", 6.0))
        placed.append({"id": c.get("id", c["key"]), "key": c["key"], "bus": c.get("bus", "fx"),
                       "t0": round(t0, 3), "t1": round(t1, 3)})
    if duck_depth:
        g = duck_gain(key, duck_depth)
        for b in cue_sheet.get("duck_buses", ["amb", "place", "music"]):
            bus[b] *= g[:, None]
    for b, db in cue_sheet.get("bus_gain", {}).items():
        bus[b] *= 10 ** (db / 20)
    return bus, placed, total


def write_wav(path, x, bits=24, rate=SR):
    """Write stereo float samples through ffmpeg (24-bit PCM, or 32-bit float with bits=32)."""
    codec = "pcm_s24le" if bits == 24 else "pcm_f32le"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(rate), "-ac", "2",
                    "-i", "-", "-c:a", codec, path],
                   input=x.astype(np.float32).tobytes(), check=True)


def measure(path):
    """Integrated loudness (LUFS), loudness range (LU) and true peak (dBTP), from ffmpeg ebur128."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-nostdin", "-i", path, "-af",
                        "ebur128=peak=true:framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True)
    out = {}
    lines = r.stderr.splitlines()
    for line in lines:
        s = line.strip()
        if s.startswith("I:") and "LUFS" in s:
            out["integrated_lufs"] = float(s.split()[1])
        elif s.startswith("LRA:") and "LU" in s:
            out["lra_lu"] = float(s.split()[1])
        elif s.startswith("Peak:") and "dBFS" in s:
            out["true_peak_dbtp"] = float(s.split()[1])
    return out


def master(mix, tmp_dir, lufs=-16.0, tp=-1.5, af=None):
    """Master EQ (`af`, an ffmpeg filter chain), gain to the loudness target, then a true-peak safe
    limiter (4x oversampled) only if needed."""
    raw = os.path.join(tmp_dir, "_premaster.wav")
    write_wav(raw, mix, bits=32)
    if af:
        eq = os.path.join(tmp_dir, "_eq.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-c:a", "pcm_f32le",
                        eq], check=True)
        raw2 = subprocess.run(["ffmpeg", "-v", "error", "-i", eq, "-f", "f32le", "-ac", "2", "-"],
                              capture_output=True, check=True).stdout
        mix = np.frombuffer(raw2, np.float32).reshape(-1, 2)[: len(mix)].copy()
        os.remove(eq)
        write_wav(raw, mix, bits=32)
    m = measure(raw)
    gain = lufs - m["integrated_lufs"]
    y = mix * 10 ** (gain / 20)
    write_wav(raw, y, bits=32)
    m2 = measure(raw)
    if m2["true_peak_dbtp"] > tp:
        lim = os.path.join(tmp_dir, "_limited.wav")
        limit = 10 ** ((tp - 0.3) / 20)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                        f"aresample=192000,alimiter=limit={limit:.4f}:attack=1:release=60:level=disabled,"
                        f"aresample={SR}", "-c:a", "pcm_f32le", lim], check=True)
        raw2 = subprocess.run(["ffmpeg", "-v", "error", "-i", lim, "-f", "f32le", "-ac", "2", "-"],
                              capture_output=True, check=True).stdout
        y = np.frombuffer(raw2, np.float32).reshape(-1, 2)[: len(mix)].copy()
        os.remove(lim)
        MASTER_NOTES["limiter_in_dbtp"] = m2["true_peak_dbtp"]
        # the limiter took a little loudness: give back what keeps the true peak under the ceiling
        write_wav(raw, y, bits=32)
        m3 = measure(raw)
        back = min(lufs - m3["integrated_lufs"], tp - m3["true_peak_dbtp"] - 0.1)
        if back > 0:
            y = y * 10 ** (back / 20)
    os.remove(raw)
    return y


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2

    def opt(name, default):
        return argv[argv.index(name) + 1] if name in argv else default

    src_dir, out_dir = argv[0], argv[1]
    os.makedirs(out_dir, exist_ok=True)
    cue_sheet = json.load(open(opt("--cues", os.path.join(HERE, "cues.json"))))
    timeline = json.load(open(opt("--timeline", os.path.join(HERE, "shots.default.json"))))
    bus, placed, total = build(cue_sheet, timeline, src_dir)
    stems = os.path.join(out_dir, "stems")
    os.makedirs(stems, exist_ok=True)
    for b, x in bus.items():
        write_wav(os.path.join(stems, f"{b}.wav"), x, bits=32)
    mix = sum(bus.values())
    mix = master(mix, out_dir, float(opt("--lufs", -16)), float(opt("--tp", -1.5)),
                 cue_sheet.get("master_af"))
    n = len(mix)
    edge = int(0.02 * SR)  # no step at either end
    mix[:edge] *= fade_curve(edge, "in")[:, None]
    mix[n - edge:] *= fade_curve(edge, "out")[:, None]
    wav = os.path.join(out_dir, "teaser_mix.wav")
    write_wav(wav, mix, bits=24)
    m4a = os.path.join(out_dir, "teaser_mix.m4a")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-c:a", "aac", "-b:a", "256k",
                    "-movflags", "+faststart", m4a], check=True)
    report = {"duration_s": round(n / SR, 3), "wav": measure(wav), "m4a": measure(m4a),
              "clipped_samples": int((np.abs(mix) >= 0.9999).sum()), "master": MASTER_NOTES,
              "cues": placed}
    video = opt("--video", None)
    if video:
        film = os.path.join(out_dir, "teaser_with_sound.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", m4a, "-map", "0:v:0",
                        "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy", "-shortest",
                        "-movflags", "+faststart", film], check=True)
        report["film"] = film
    json.dump(report, open(os.path.join(out_dir, "report.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "cues"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

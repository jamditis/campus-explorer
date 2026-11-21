// Print the film's clock as JSON for the sound mix: shots (name, start, duration in seconds, the 3D
// graphics with their in/out times) and named markers, read from ../storyboard.mjs.
//   node tools/teaser/sound/timeline.mjs > /tmp/timeline.json
// Shot starts use the capture's own frame rounding (path.mjs timeline), so sound and picture agree
// to the frame. Markers: storyboard.markers as { name: seconds } or [{ name, shot, at }] or
// [{ name, frame }]; anything else in the storyboard is ignored.
import { storyboard } from '../storyboard.mjs';
import { timeline } from '../path.mjs';

const { fps, shots } = storyboard;
const { starts, frames } = timeline(shots, fps);
const startOf = name => {
  const i = shots.findIndex(s => s.name === name);
  if (i < 0) throw new Error(`marker names unknown shot ${name}`);
  return starts[i] / fps;
};
const out = {
  fps,
  total: frames / fps,
  shots: shots.map((s, i) => ({
    name: s.name,
    start: starts[i] / fps,
    duration: Math.round(s.duration * fps) / fps,
    time: s.time ?? null,
    time2: s.time2 ?? null,
    graphics: (s.graphics ?? []).map(g => ({
      id: g.id, kind: g.kind, text: g.text ?? null,
      in: g.in ?? 0, inDur: g.inDur ?? 0.6, out: g.out ?? null, outDur: g.outDur ?? 0.4,
    })),
  })),
  markers: {},
};
const m = storyboard.markers ?? {};
if (Array.isArray(m)) {
  for (const k of m) {
    if (k.frame !== undefined) out.markers[k.name] = k.frame / fps;
    else out.markers[k.name] = startOf(k.shot) + (k.at ?? 0);
  }
} else {
  for (const [name, v] of Object.entries(m)) {
    out.markers[name] = typeof v === 'number' ? v : v.frame !== undefined ? v.frame / fps : startOf(v.shot) + (v.at ?? 0);
  }
}
console.log(JSON.stringify(out, null, 1));

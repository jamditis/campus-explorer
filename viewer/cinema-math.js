// The film: a fixed list of camera shots over the campus and the view east, each an eased move from one
// pose to another at a chosen light, with cuts between them. Pure, no imports from three: viewer/cinema.js
// plays it. Positions are viewer metres (x east, y up, -z grid north); a shot with `ground` gives its heights
// above the ground there, found when the shot starts.

const DEG = Math.PI / 180;
// Midtown Manhattan from the campus: bearing 124 degrees (true; grid north is 0.2 degrees off, not worth it here)
const EAST = [Math.sin(124 * DEG), 0, -Math.cos(124 * DEG)];
const toward = (p, dir, d, dy) => [p[0] + dir[0] * d, p[1] + dy, p[2] + dir[2] * d];

/** Light for a shot: 'golden' is 35 minutes before sunset, 'night' 100 minutes after, on the date shown. */
export const LIGHT = { golden: -35, night: 100 };

/**
 * The shots, in order. `from` and `to` are { position, target }; `seconds` the length of the move.
 * `ground` [x, z]: y values are metres above the ground there. Captions are plain place names. Every target sits
 * below its camera: orbit mode keeps the camera above its target.
 */
export const SHOTS = [
  {
    caption: 'Montclair State University', light: 'golden', seconds: 11,
    from: { position: [360, 330, 260], target: [-45, 120, 60] },
    to: { position: [150, 290, 450], target: [-45, 120, 60] },
  },
  {
    caption: 'Toward Manhattan, 20 km east', light: 'golden', seconds: 11, ground: [150, -300],
    from: { position: [100, 70, -330], target: toward([100, 70, -330], EAST, 1500, -45) },
    to: { position: [200, 95, -265], target: toward([200, 95, -265], EAST, 1500, -55) },
  },
  {
    caption: 'Susan A. Cole Hall', light: 'golden', seconds: 9, ground: [-200, 88],
    from: { position: [-204, 1.7, 92], target: [-150, 1.2, 96] },
    to: { position: [-189, 1.7, 93.5], target: [-150, 1.2, 96] },
  },
  {
    caption: 'The skyline after dark', light: 'night', seconds: 13, ground: [150, -300],
    from: { position: [200, 95, -265], target: toward([200, 95, -265], EAST, 1500, -55) },
    to: { position: [110, 150, -370], target: toward([110, 150, -370], EAST, 1500, -60) },
  },
];

/** Smootherstep: starts and ends at rest, no jolt. */
export function ease(t) {
  const x = Math.min(1, Math.max(0, t));
  return x * x * x * (x * (x * 6 - 15) + 10);
}

const lerp3 = (a, b, k) => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
const lift = (p, y) => [p[0], p[1] + y, p[2]];

/**
 * The camera pose `t` seconds into a shot. `groundY` is the ground height at shot.ground (ignored without it).
 * `still` (reduced motion) holds the shot's end pose.
 * @returns {{ position: number[], target: number[] }}
 */
export function poseAt(shot, t, groundY = 0, still = false) {
  const k = still ? 1 : ease(t / shot.seconds), y = shot.ground ? groundY : 0;
  return {
    position: lift(lerp3(shot.from.position, shot.to.position, k), y),
    target: lift(lerp3(shot.from.target, shot.to.target, k), y),
  };
}

/** Minutes from sunset for a shot's light, or null to keep the time shown. */
export const lightOffset = shot => LIGHT[shot.light] ?? null;

/** Height in CSS pixels of each letterbox bar that frames a width x height view at `aspect` (2.39:1). */
export function letterbox(width, height, aspect = 2.39) {
  return Math.max(0, Math.round((height - width / aspect) / 2));
}

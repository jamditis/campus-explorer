// Pure. The rules of the ownership map that joins the two source models into one campus.
// One definition for the tool that writes the map (tools/web-export/unify.mjs), the shaders that
// hide pixels (look.js) and collision (viewer/world.js), so the three cannot drift apart.

/** Byte stored per 2 m cell of ground. Border cells are drawn by both neighbours so no gap opens. */
export const VALUE = Object.freeze({ none: 0, northEdge: 100, north: 128, mainEdge: 228, main: 255 });

// What each model hides, as an open range of the stored value scaled to 0..1 (what a shader reads).
// Ranges, not exact values, so a browser that shifts a grey level by one on decode changes nothing.
const HIDE = Object.freeze({
  main: [0.3, 0.6],    // the north model's cells, border included
  north: [0.95, 2],    // the main model's cells, except its border
  skirt: [0.45, 0.55], // the north model's cells, except its border
});

/** Does `group` ('main', 'north' or 'skirt') hide its surfaces where the map reads `o` (0..1)? */
export function hidden(group, o) {
  const r = HIDE[group];
  return !!r && o > r[0] && o < r[1];
}

/** Does `group` draw, and so stay solid, in a cell holding the byte `value`? */
export const shows = (group, value) => !hidden(group, value / 255);

/** The same test as GLSL on a float `o`, for the fragment shaders. */
export function glslTest(group) {
  const [lo, hi] = HIDE[group];
  return `o > ${lo.toFixed(3)} && o < ${hi.toFixed(3)}`;
}

export const GROUPS = Object.freeze(Object.keys(HIDE));

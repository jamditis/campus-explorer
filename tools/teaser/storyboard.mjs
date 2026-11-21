// The teaser's storyboard: shots, camera keys, light, the 3D graphics, the grade and the hit points.
// capture.mjs films it, finish.py grades it, sound/timeline.mjs gives its clock to the sound mix.
//
// Frame: viewer metres, x east, y up, z = -north (grid). With `rel: true` the y of every key, graphic
// and shadow focus is metres above the ground at that x, z (looked up in the loaded model).
// Times are real instants in Montclair (the viewer's sun model); `time2` sweeps the light.
// Every number on screen is checked against the repository (see FACTS); places use the university's
// names as in viewer/places.json (OpenStreetMap).
import { ease } from './path.mjs';

/** Facts shown on screen, with where each comes from. */
export const FACTS = {
  places: { text: '90 named places', from: 'viewer/places.json: places.length = 90 (OpenStreetMap)' },
  rooms: { text: '41 rooms', from: 'viewer/rooms.json: rooms.length = 41 (floor signs)' },
  tiles: { text: '63 squares of 160 m', from: 'models/main/manifest.json: 63 distinct non-empty tile centres, 160 m tiles (README)' },
  area: { text: '1.6 km²', from: '63 × 0.16 km × 0.16 km = 1.61 km²' },
  size: { text: '180 MB', from: 'models/main/manifest.json: total_bytes = 180,213,896' },
  sources: { text: 'USGS 3DEP LiDAR · NJ 2020 orthoimagery · OpenStreetMap', from: 'README.md, Data sources' },
  tools: { text: 'Blender · three.js', from: 'README.md' },
  name: { text: 'Campus explorer', from: 'README.md title' },
  url: { text: 'jamditis.github.io/campus-explorer', from: 'README.md, live viewer' },
};

// One evening, late afternoon to blue hour (the sun model is the viewer's, for 22 September 2026).
const OPEN = '2026-09-22T17:35:00-04:00'; // sun 258° (west), 14° up
const GOLD = '2026-09-22T17:55:00-04:00'; // sun 261°, 10° up: the College of Communication and Media's west front lit
const LOW = '2026-09-22T18:10:00-04:00'; // sun 263°, 7.5° up: long shadows
const SET = '2026-09-22T18:40:00-04:00'; // sun 268°, 1.8° up
const BLUE = '2026-09-22T19:14:00-04:00'; // sun 5° below: lamps coming on
const fade = (a, b) => sec => ease.smooth((sec - a) / (b - a));
const unfade = (a, b) => sec => 1 - ease.smooth((sec - a) / (b - a));

// The move into the College of Communication and Media: down from over the library roof to the plaza,
// level with the arched entrance, through its glass and on into the atrium toward the stair.
// Absolute heights (the atrium floor is 137.3, the plaza about 137).
const CCM = {
  duration: 9, accel: 0.22, decel: 0.3,
  pos: [[-78, 158, -62], [-56, 149, -40], [-40, 141.5, -18], [-30, 139.8, -9.6], [-20, 139.7, -8.9], [-12, 139.9, -9.4], [-7, 140.6, -8]],
  look: [[-21, 146, -8.5], [-21, 144, -8.5], [-10, 141, -8.5], [0, 140.2, -9], [4, 140.4, -7], [4, 141.6, -4], [3, 142.8, -1]],
  fov: 40, fov2: 54, drift: 0.03,
};

// typographic system: Inter Display, two weights; sizes are em heights in metres by role and distance
const T = {
  title: { font: 'semibold', tracking: -0.01, bevel: 0.01 },
  name: { font: 'semibold', tracking: 0 },
  note: { font: 'regular', tracking: 0.01 },
};

export const storyboard = {
  fps: 24,
  width: 1280,
  height: 720,
  grades: {
    // per sequence; finish.py: warm (+ warmer), sat, contrast, lift [r,g,b], gamma, gain, vignette, grain, bloom
    ui: { warm: 0, sat: 1, contrast: 0, vignette: 0, grain: 0, bloom: 0 },
    morning: { warm: 0.6, sat: 1.04, contrast: 0.14, lift: [0.015, 0.012, 0.02], gamma: 1.02, vignette: 0.24, grain: 0.016, bloom: 0.3 },
    interior: { warm: 0.9, sat: 1.0, contrast: 0.12, lift: [0.02, 0.015, 0.01], gamma: 1.05, vignette: 0.28, grain: 0.02, bloom: 0.2 },
    day: { warm: 0.4, sat: 1.06, contrast: 0.14, lift: [0.01, 0.01, 0.015], vignette: 0.22, grain: 0.016, bloom: 0.25 },
    gold: { warm: 1.0, sat: 1.08, contrast: 0.16, lift: [0.02, 0.012, 0.0], vignette: 0.26, grain: 0.016, bloom: 0.35 },
    blue: { warm: -0.6, sat: 1.0, contrast: 0.14, lift: [0.0, 0.01, 0.03], gamma: 1.04, vignette: 0.3, grain: 0.022, bloom: 0.5 },
  },
  shots: [
    {
      // the real interface: a visitor types a place into the search box; then the interface dissolves,
      // the film frame and grade come in, and the camera starts to move
      name: 'ui_open', duration: 4.0, grade: 'morning', time: MORNING, rel: true, ui: unfade(2.3, 3.3),
      film: fade(2.6, 4.0), accel: 0.9, decel: 0,
      typed: sec => 'College of Communication and Media'.slice(0, Math.max(0, Math.floor((sec - 0.4) * 16))),
      pos: [[700, 520, 700], [690, 512, 690]], look: [[-120, 0, -450], [-120, 0, -450]], fov: 42,
      shadow: { focus: [-60, 0, -200], half: 900 },
    },
    {
      // high over the campus in early light, slow push in; the title stands on the Alumni Green
      name: 'dawn_wide', duration: 5.0, grade: 'morning', time: MORNING, rel: true, accel: 0, decel: 0.5,
      pos: [[690, 512, 690], [560, 380, 520], [430, 270, 380]], look: [[-120, 0, -450], [-110, 0, -300], [-100, 0, -120]],
      fov: 42, fov2: 38, shadow: { focus: [-60, 0, -200], half: 900 },
      graphics: [
        { id: 'title_main', kind: 'text', text: 'Montclair State University', ...T.title, size: 26, depth: 4, at: [-105, 0, 40], yaw: 0.65, in: 1.0, inDur: 1.0, out: 4.8, outDur: 0.4 },
        { id: 'title_sub', kind: 'text', text: 'an open 3D model from free public data', ...T.note, size: 9, depth: 1.5, at: [-80, 0, 75], yaw: 0.65, in: 1.8, inDur: 0.8, out: 4.8, outDur: 0.4 },
      ],
    },
    {
      // a low glide in to the College of Communication and Media past the trees; its name stands on the lawn
      name: 'ccm_glide', duration: 4.5, grade: 'morning', time: MORNING, rel: true, accel: 0.25, decel: 0.15,
      pos: [[-110, 14, -40], [-80, 7, -20], [-48, 3.5, -10]], look: [[-10, 10, 0], [0, 9, -5], [-20, 3.5, -8]],
      fov: 40, fov2: 48, shadow: { focus: [-40, 0, -10], half: 90 },
      graphics: [
        { id: 'title_ccm', kind: 'text', text: 'College of Communication and Media', ...T.name, size: 3.4, depth: 0.6, at: [-62, 0, 6], yaw: -1.2, in: 0.5, inDur: 0.8, out: 3.9, outDur: 0.4 },
        { id: 'dim_ccm', kind: 'dim', a: [-36, 0, 22], b: [-36, 11, 22], head: 0.9, tick: 0.8, width: 0.16, up: [0, 0, 1], in: 1.2, inDur: 0.8, out: 3.9, outDur: 0.3 },
      ],
    },
    {
      // through the entrance glass into the double-height atrium; a handheld drift up toward the stair
      name: 'atrium', duration: 4.5, grade: 'interior', time: MORNING, rel: false, accel: 0, decel: 0.5, drift: 0.05,
      pos: [[-30, 139.6, -8.5], [-18, 139.4, -9], [-8, 140.6, -10.5]], look: [[0, 139.8, -9], [5, 140.2, -10], [6, 142.6, -2]],
      fov: 52, fov2: 58, shadow: { focus: [-20, 137, -8], half: 60 },
      graphics: [
        { id: 'room_2012', kind: 'text', text: '2012', ...T.name, size: 0.7, depth: 0.08, bevel: 0.006, at: [-5.47, 143.0, -0.69], yaw: -1.6, in: 2.4, inDur: 0.6, out: 4.4, outDur: 0.2, rise: 'extrude' },
        { id: 'title_rooms', kind: 'text', text: '41 rooms', ...T.note, size: 0.5, depth: 0.06, bevel: 0.004, at: [-5.4, 142.3, -0.7], yaw: -1.6, in: 2.8, inDur: 0.6, out: 4.4, outDur: 0.2, rise: 'extrude' },
      ],
    },
    {
      // the Alumni Green: a crane rise that reveals Susan A. Cole Hall, in high morning light
      name: 'green', duration: 4.5, grade: 'day', time: NOON, rel: true, accel: 0.3, decel: 0.4,
      pos: [[-60, 3, 10], [-62, 18, 0], [-66, 40, -12]], look: [[-110, 6, 60], [-112, 8, 80], [-114, 6, 95]],
      fov: 38, shadow: { focus: [-100, 0, 55], half: 140 },
      graphics: [
        { id: 'title_green', kind: 'text', text: 'Alumni Green', ...T.name, size: 5, depth: 0.9, at: [-98, 0, 40], yaw: -0.8, in: 0.4, inDur: 0.8, out: 4.3, outDur: 0.3 },
        { id: 'pin_cole', kind: 'pin', at: [-113, 22, 95], height: 10, radius: 0.35, in: 1.6, inDur: 0.6, out: 4.3, outDur: 0.3 },
        { id: 'title_cole', kind: 'text', text: 'Susan A. Cole Hall', ...T.note, size: 3.2, depth: 0.5, at: [-113, 35, 95], yaw: -0.6, in: 1.9, inDur: 0.6, out: 4.3, outDur: 0.3 },
      ],
    },
    {
      // one continuous move, south-west to north: the station, Sprague Field, up the ridge to the stadium,
      // the decks and the Village. A dimension line on the ground measures the run.
      name: 'travel', duration: 9.0, grade: 'day', time: AFTERNOON, rel: true, accel: 0.18, decel: 0.2,
      pos: [[-560, 70, 380], [-420, 110, 120], [-250, 150, -350], [-60, 150, -800], [-20, 170, -1150], [-60, 200, -1420]],
      look: [[-454, 0, 262], [-330, 0, 100], [-150, 0, -500], [80, 0, -960], [-120, 0, -1180], [-200, 0, -1600]],
      fov: 46, fov2: 40, shadow: { focus: [-200, 0, -600], half: 1100 },
      graphics: [
        { id: 'dim_travel', kind: 'dim', a: [-454, 2, 262], b: [-200, 2, -1460], head: 24, tick: 14, width: 3.2, up: [0.98, 0, 0.2], in: 0.6, inDur: 2.4, out: 8.6, outDur: 0.4 },
        { id: 'title_travel', kind: 'text', text: '1.7 km', ...T.title, size: 40, depth: 5, at: [-250, 2, -600], yaw: 0.6, flat: true, in: 3.2, inDur: 1.0, out: 8.6, outDur: 0.4, rise: 'extrude' },
      ],
    },
    {
      // long lens over the ridge to the Manhattan skyline as the light goes; lamps come on
      name: 'dusk', duration: 6.0, grade: 'blue', time: GOLD, time2: BLUE, timeFrom: 0.05, timeTo: 0.8, rel: true,
      accel: 0.4, decel: 0.4, pos: [[-260, 85, -40], [-250, 88, -60]], look: [[2000, 40, 300], [2000, 40, 280]],
      fov: 20, fov2: 18, shadow: { focus: [0, 0, 0], half: 600 },
      graphics: [
        { id: 'title_skyline', kind: 'text', text: '90 named places · 41 rooms · 1.6 km²', ...T.note, size: 7, depth: 1, at: [-60, 30, -20], yaw: -1.45, in: 3.2, inDur: 0.8, out: 5.8, outDur: 0.3 },
      ],
    },
    {
      // the end title stands over the campus at blue hour
      name: 'end_title', duration: 3.5, grade: 'blue', time: BLUE, rel: true, accel: 0.4, decel: 0.6,
      pos: [[-640, 360, 520], [-610, 345, 490]], look: [[-100, 0, -350], [-100, 0, -350]], fov: 40,
      shadow: null,
      graphics: [
        { id: 'title_end', kind: 'text', text: 'Campus explorer', ...T.title, size: 34, depth: 5, at: [-230, 30, 0], yaw: -0.85, in: 0.3, inDur: 1.0 },
        { id: 'title_url', kind: 'text', text: 'jamditis.github.io/campus-explorer', ...T.note, size: 11, depth: 1.5, at: [-205, 6, 30], yaw: -0.85, in: 1.0, inDur: 0.8 },
      ],
    },
    {
      // the film frame eases out and the real interface returns over the same view: it all runs in the browser
      name: 'ui_close', duration: 4.0, grade: 'blue', time: BLUE, rel: true, still: false,
      film: unfade(0.2, 1.4), ui: fade(0.6, 1.6), accel: 0, decel: 1,
      pos: [[-610, 345, 490], [-606, 343, 486]], look: [[-100, 0, -350], [-100, 0, -350]], fov: 40,
      graphics: [
        { id: 'title_end', kind: 'text', text: 'Campus explorer', ...T.title, size: 34, depth: 5, at: [-230, 30, 0], yaw: -0.85, in: -5 },
        { id: 'title_url', kind: 'text', text: 'jamditis.github.io/campus-explorer', ...T.note, size: 11, depth: 1.5, at: [-205, 6, 30], yaw: -0.85, in: -5 },
      ],
    },
  ],
  // hit points for the sound (seconds into a shot)
  markers: [
    { name: 'keypress', shot: 'ui_open', at: 0.4 },
    { name: 'ui_fade', shot: 'ui_open', at: 2.3 },
    { name: 'glass', shot: 'atrium', at: 1.1 },
    { name: 'stair', shot: 'atrium', at: 2.6 },
    { name: 'glass_out', shot: 'atrium', at: 4.4 },
    { name: 'travel_start', shot: 'travel', at: 0 },
    { name: 'station', shot: 'travel', at: 0.6 },
    { name: 'sprague', shot: 'travel', at: 2.0 },
    { name: 'stadium', shot: 'travel', at: 5.2 },
    { name: 'decks', shot: 'travel', at: 6.4 },
    { name: 'travel_peak', shot: 'travel', at: 4.2 },
    { name: 'village', shot: 'travel', at: 7.6 },
    { name: 'dusk_turn', shot: 'dusk', at: 0.3 },
    { name: 'lamps', shot: 'dusk', at: 3.6 },
    { name: 'skyline', shot: 'dusk', at: 2.0 },
    { name: 'ui_return', shot: 'ui_close', at: 0.6 },
  ],
};

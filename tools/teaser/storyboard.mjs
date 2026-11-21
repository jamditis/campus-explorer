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
  tiles: { text: '67 squares of 160 m', from: 'models/main/manifest.json (sw12, exported November 20, 2026, 9:07 PM ET): 67 distinct non-empty tile centres; 160 m tiles (README)' },
  area: { text: '1.7 km²', from: '67 × 0.16 km × 0.16 km = 1.72 km²' },
  size: { text: '186 MB', from: 'models/main/manifest.json: total_bytes = 185,605,520' },
  stations: { text: '1.4 km station to station', from: 'viewer/places.json at 17c0170 (OpenStreetMap): Montclair Heights station (-454, 266), Montclair State University station (-28, -1063): 1,396 m' },
  sources: { text: 'USGS 3DEP LiDAR · NJ 2020 orthoimagery · OpenStreetMap', from: 'README.md, Data sources' },
  tools: { text: 'Blender · three.js', from: 'README.md' },
  name: { text: 'Campus explorer', from: 'README.md title' },
  url: { text: 'jamditis.github.io/campus-explorer', from: 'README.md, live viewer' },
};

// One evening, late afternoon to blue hour (the sun model is the viewer's, for 22 September 2026).
const OPEN = '2026-09-22T17:35:00-04:00'; // sun 258° (west), 14° up
const GOLD = '2026-09-22T17:55:00-04:00'; // sun 261°, 10° up: the College of Communication and Media's west front lit
const LOW = '2026-09-22T18:10:00-04:00'; // sun 263°, 7.5° up: long shadows
const AFT = '2026-09-22T17:25:00-04:00'; // sun 256°, 16° up: the long travelling shot, shadows open
const SET = '2026-09-22T18:40:00-04:00'; // sun 268°, 1.8° up
const BLUE = '2026-09-22T19:14:00-04:00'; // sun 5° below: lamps coming on
const DUSK = '2026-09-22T19:04:00-04:00'; // sun 3° below: the end card
const fade = (a, b) => sec => ease.smooth((sec - a) / (b - a));
const unfade = (a, b) => sec => 1 - ease.smooth((sec - a) / (b - a));

// The move into the College of Communication and Media: down from over the library roof to the plaza,
// level with the arched entrance, through its glass and on into the atrium toward the stair.
// Absolute heights (the atrium floor is 137.3, the plaza about 137).
const CCM = {
  duration: 9, accel: 0.22, decel: 0.3,
  // stays above the library roof (about 149) until past its east wall, then drops to the plaza; the
  // entrance doors' centre is at z -10.5 (measured on the animatic frames)
  pos: [[-78, 160, -62], [-56, 155.5, -41], [-44, 150.5, -27], [-35, 143, -16], [-28.5, 139.9, -11], [-20, 139.75, -10.5], [-13, 139.85, -11], [-8, 140.4, -11.8]],
  look: [[-21, 146, -10.5], [-21, 144.5, -10.5], [-15, 142, -10.5], [-5, 140.6, -10.5], [2, 140.3, -10.5], [4, 140.5, -12], [3, 140.8, -16], [0, 141, -20]],
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
    travel: { warm: 0.45, sat: 1.08, contrast: 0.1, lift: [0.035, 0.035, 0.04], gamma: 1.18, gain: 1.08, vignette: 0.2, grain: 0.016, bloom: 0.25 },
    day: { warm: 0.4, sat: 1.06, contrast: 0.14, lift: [0.01, 0.01, 0.015], vignette: 0.22, grain: 0.016, bloom: 0.25 },
    gold: { warm: 0.7, sat: 1.12, contrast: 0.15, lift: [0.015, 0.01, 0.0], vignette: 0.24, grain: 0.016, bloom: 0.35 },
    blue: { warm: -0.5, sat: 1.0, contrast: 0.14, lift: [0.0, 0.01, 0.03], gamma: 1.25, gain: 1.5, vignette: 0.3, grain: 0.022, bloom: 0.5 },
  },
  shots: [
    {
      // the real interface as a visitor sees it; the search box is typed for real. The interface
      // dissolves, the film frame and the grade come in; the camera is still (one draw for 4 s)
      name: 'ui_open', duration: 4.0, grade: 'gold', time: OPEN, rel: true, ui: unfade(2.3, 3.3), film: fade(2.5, 4.0),
      typed: sec => 'College of Communication and Media'.slice(0, Math.max(0, Math.floor((sec - 0.3) * 20))),
      pos: [[-250, 380, 700], [-250, 380, 700]], look: [[-100, 0, -150], [-100, 0, -150]], fov: 42,
      shadow: { focus: [-110, 0, -60], half: 900 },
    },
    {
      // a drone descends over the campus toward the Alumni Green, where the title stands among the trees
      name: 'dawn_wide', duration: 5.0, grade: 'gold', time: OPEN, rel: true, accel: 0.45, decel: 0.35,
      pos: [[-250, 380, 700], [-215, 290, 520], [-175, 195, 335]], look: [[-100, 0, -150], [-104, 0, -20], [-105, 0, 40]],
      fov: 42, fov2: 38, shadow: { focus: [-110, 0, -60], half: 900 },
      graphics: [
        { id: 'title_main', kind: 'text', text: 'Montclair State University', ...T.title, colour: 'lit', size: 21, depth: 3.5, at: [-106, 12, 30], yaw: -0.22, tilt: -0.42, rise: 'scale', in: 1.3, inDur: 1.1, out: 4.75, outDur: 0.25 },
        { id: 'title_sub', kind: 'text', text: 'an open 3D model from free public data', ...T.name, colour: 'lit', size: 9, depth: 1.4, at: [-101, 5, 66], yaw: -0.22, tilt: -0.42, rise: 'scale', in: 2.1, inDur: 0.9, out: 4.75, outDur: 0.25 },
      ],
    },
    {
      // down from over the library roof to the plaza; the college's name stands along its west front
      name: 'ccm_glide', duration: 4.5, grade: 'gold', time: GOLD, rel: false, move: CCM, span: [0, 0.5],
      shadow: { focus: [-30, 137, -15], half: 80 },
      graphics: [
        { id: 'title_ccm', kind: 'text', text: 'College of Communication and Media', ...T.name, size: 1.0, depth: 0.2, at: [-27.5, 0.1, -20.5], rel: true, yaw: -2.25, tilt: -0.3, in: 0.8, inDur: 0.9, out: 4.5, outDur: 0.01 },
      ],
    },
    {
      // through the entrance glass into the double-height atrium, drifting toward the stair; a room on floor 2
      name: 'atrium', duration: 4.5, grade: 'interior', time: GOLD, rel: false, move: CCM, span: [0.5, 0.8],
      shadow: { focus: [-30, 137, -15], half: 80 },
      graphics: [
        { id: 'title_ccm', kind: 'text', text: 'College of Communication and Media', ...T.name, size: 1.0, depth: 0.2, at: [-27.5, 0.1, -20.5], rel: true, yaw: -2.25, tilt: -0.3, in: -9, out: 0.8, outDur: 0.5 },
      ],
    },
    {
      // a crane rise past Kasser Theater's plaza over the Alumni Green, low sun behind; Cole Hall pinned
      name: 'green', duration: 4.5, grade: 'gold', time: LOW, rel: true, accel: 0.35, decel: 0.4,
      pos: [[-182, 3, 50], [-178, 14, 45], [-170, 32, 38]], look: [[-100, 6, 52], [-98, 4, 56], [-95, 0, 60]],
      fov: 38, shadow: { focus: [-130, 0, 55], half: 170 },
      graphics: [
        { id: 'title_green', kind: 'text', text: 'Alumni Green', ...T.name, size: 4.2, depth: 0.7, at: [-112, 0, 38], yaw: -1.49, in: 0.5, inDur: 0.9, out: 4.3, outDur: 0.2 },
        { id: 'pin_cole', kind: 'pin', at: [-113, 20, 95], height: 9, radius: 0.32, in: 1.7, inDur: 0.6, out: 4.3, outDur: 0.2 },
        { id: 'title_cole', kind: 'text', text: 'Susan A. Cole Hall', ...T.note, size: 2.6, depth: 0.4, at: [-113, 32.5, 95], yaw: -1.35, rise: 'scale', in: 2.0, inDur: 0.6, out: 4.3, outDur: 0.2 },
      ],
    },
    {
      // one continuous move from Montclair Heights station up the ridge past Sprague Field, the stadium and
      // the decks to the Village; a measured line joins the campus's two stations
      name: 'travel', duration: 9.0, grade: 'travel', time: AFT, rel: true, accel: 0.2, decel: 0.22,
      pos: [[-600, 85, 420], [-470, 105, 160], [-300, 130, -260], [-170, 150, -700], [-90, 150, -990]],
      look: [[-454, 0, 266], [-336, 0, 100], [-150, 0, -560], [40, 0, -960], [-165, 0, -1160]],
      fov: 46, fov2: 42, shadow: { focus: [-260, 0, -480], half: 1000 },
      graphics: [
        { id: 'dim_travel', kind: 'dim', a: [-454, 30, 266], b: [-28, 30, -1063], head: 26, tick: 18, width: 1.6, every: 100, colour: 'lit', headColour: 'red', up: [0, 1, 0], in: 0.7, inDur: 2.6, out: 8.7, outDur: 0.3 },
        { id: 'title_travel', kind: 'text', text: '1.4 km station to station', ...T.title, colour: 'lit', size: 14, depth: 2.2, at: [-110, 70, -560], yaw: -0.46, tilt: -0.3, rise: 'scale', in: 2.0, inDur: 0.9, out: 5.4, outDur: 0.3 },
      ],
    },
    {
      // a long lens from the north-west: the College of Communication and Media's tower in the last sun
      // against the Manhattan skyline as the light goes blue; a slow sideways drift for parallax
      name: 'dusk', duration: 6.0, grade: 'blue', time: SET, time2: BLUE, timeFrom: 0.1, timeTo: 0.9, rel: false,
      accel: 0.4, decel: 0.4, pos: [[-296, 187, -190], [-284, 186, -205]], look: [[-21, 165, -12], [-21, 164.5, -12]],
      fov: 13, fov2: 11.5, shadow: { focus: [-60, 140, -60], half: 260 },
    },
    {
      // the end title stands over the campus at blue hour
      name: 'end_title', duration: 3.5, grade: 'blue', time: DUSK, rel: true, accel: 0.3, decel: 0.7,
      pos: [[-660, 370, 540], [-640, 360, 520]], look: [[-100, 0, -350], [-100, 0, -350]], fov: 40,
      graphics: [
        { id: 'title_end', kind: 'text', text: 'Campus explorer', ...T.title, colour: 'lit', size: 66, depth: 8, at: [-235, 22, -132], yaw: -0.556, tilt: -0.35, rise: 'scale', in: 0.3, inDur: 1.1 },
        { id: 'title_url', kind: 'text', text: 'jamditis.github.io/campus-explorer', ...T.note, colour: 'lit', size: 27, depth: 3, at: [-275, 8, -68], yaw: -0.556, tilt: -0.35, rise: 'scale', in: 1.0, inDur: 0.9 },
        { id: 'title_facts', kind: 'text', text: '90 named places · 41 rooms · 1.7 km² · free public data', ...T.note, colour: 'lit', size: 12.5, depth: 1.5, at: [-312, 3, -10], yaw: -0.556, tilt: -0.35, rise: 'scale', in: 1.6, inDur: 0.8 },
      ],
    },
    {
      // the film frame eases out and the real interface returns over the same view: it all runs in the browser
      name: 'ui_close', duration: 4.0, grade: 'blue', time: DUSK, rel: true,
      film: unfade(0.3, 1.5), ui: fade(0.8, 1.8),
      pos: [[-640, 360, 520], [-640, 360, 520]], look: [[-100, 0, -350], [-100, 0, -350]], fov: 40,
      graphics: [
        { id: 'title_end', kind: 'text', text: 'Campus explorer', ...T.title, colour: 'lit', size: 66, depth: 8, at: [-235, 22, -132], yaw: -0.556, tilt: -0.35, rise: 'scale', in: -9 },
        { id: 'title_url', kind: 'text', text: 'jamditis.github.io/campus-explorer', ...T.note, colour: 'lit', size: 27, depth: 3, at: [-275, 8, -68], yaw: -0.556, tilt: -0.35, rise: 'scale', in: -9 },
        { id: 'title_facts', kind: 'text', text: '90 named places · 41 rooms · 1.7 km² · free public data', ...T.note, colour: 'lit', size: 12.5, depth: 1.5, at: [-312, 3, -10], yaw: -0.556, tilt: -0.35, rise: 'scale', in: -9 },
      ],
    },
  ],
  // hit points for the sound (seconds into a shot)
  markers: [
    { name: 'keypress', shot: 'ui_open', at: 0.3 },
    { name: 'ui_fade', shot: 'ui_open', at: 2.3 },
    { name: 'title_main_land', shot: 'dawn_wide', at: 2.4 },
    { name: 'glass', shot: 'atrium', at: 0.5 },
    { name: 'stair', shot: 'atrium', at: 2.4 },
    { name: 'glass_out', shot: 'atrium', at: 4.5 },
    { name: 'travel_start', shot: 'travel', at: 0 },
    { name: 'station', shot: 'travel', at: 0.5 },
    { name: 'sprague', shot: 'travel', at: 1.9 },
    { name: 'travel_peak', shot: 'travel', at: 4.0 },
    { name: 'stadium', shot: 'travel', at: 5.4 },
    { name: 'decks', shot: 'travel', at: 6.6 },
    { name: 'village', shot: 'travel', at: 8.2 },
    { name: 'dusk_turn', shot: 'dusk', at: 0.3 },
    { name: 'skyline', shot: 'dusk', at: 0.5 },
    { name: 'lamps', shot: 'dusk', at: 5.0 },
    { name: 'title_end_land', shot: 'end_title', at: 1.4 },
    { name: 'ui_return', shot: 'ui_close', at: 0.8 },
  ],
};

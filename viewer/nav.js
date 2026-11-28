// Navigation HUD for walking directions: a glowing ribbon on the ground ahead of the walker, a direction
// arrow, the next turn, the distance and time left, and an arrival message. Follows `route` events from
// viewer/route.js. Cheap on the lite profile: one mesh with one small texture, DOM updated 5 times a second.
import * as THREE from 'three';
import { polyline, progress, pointAt, turns, nextStep, roundDistance, arrowAngle } from './nav-math.js';
import { walkMinutes } from './route-math.js';

const WIDTH = 1.4;      // ribbon width, metres
const LIFT = 0.1;       // above the ground
const DRAPE_M = 2;      // a ribbon point at least this often, so it follows the ground
const CHEVRON_M = 2.5;  // one chevron every this many metres
const AHEAD_M = 12;     // the arrow points at the route this far ahead
const ARRIVE_M = 10;    // this close to the entrance is arrival
const OFF_M = 25;       // farther than this from the route (and the GPS accuracy) for OFF_S seconds: route again
const OFF_S = 3;
const UI_MS = 200;

function chevronTexture() {
  const c = document.createElement('canvas'); c.width = 64; c.height = 64;
  const g = c.getContext('2d');
  // soft glow across the ribbon (u), bright chevron pointing along it (v up)
  const glow = g.createLinearGradient(0, 0, 64, 0);
  glow.addColorStop(0, 'rgba(70,160,255,0)'); glow.addColorStop(0.25, 'rgba(70,160,255,0.55)');
  glow.addColorStop(0.75, 'rgba(70,160,255,0.55)'); glow.addColorStop(1, 'rgba(70,160,255,0)');
  g.fillStyle = glow; g.fillRect(0, 0, 64, 64);
  g.strokeStyle = 'rgba(235,248,255,0.95)'; g.lineWidth = 9; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(16, 46); g.lineTo(32, 22); g.lineTo(48, 46); g.stroke();
  const t = new THREE.CanvasTexture(c);
  t.wrapS = THREE.ClampToEdgeWrapping; t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function createNav(app) {
  const { scene, world, player, camera } = app;
  const box = document.querySelector('.follow') ?? document.getElementById('overlay');
  const hud = document.createElement('div'); hud.className = 'nav'; hud.hidden = true; hud.setAttribute('role', 'status');
  hud.innerHTML = `<svg class="nav-arrow" viewBox="0 0 48 48" aria-hidden="true"><path d="M24 4 L40 40 L24 31 L8 40 Z"/></svg>
    <div class="nav-text"><span class="nav-step"></span><span class="nav-left"></span></div>`;
  box.append(hud);
  const arrow = hud.querySelector('.nav-arrow'), stepEl = hud.querySelector('.nav-step'), leftEl = hud.querySelector('.nav-left');

  const material = new THREE.MeshBasicMaterial({
    map: chevronTexture(), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, side: THREE.DoubleSide, fog: false, toneMapped: false,
  });
  let mesh = null, nav = null, lastUi = 0, offSince = 0, arrived = false;

  function ribbon(points) {
    // drape: a point every DRAPE_M at the surface under it
    const flat = [];
    for (let k = 0; k < points.length; k++) {
      if (!k) { flat.push(points[0]); continue; }
      const [x0, z0] = points[k - 1], [x1, z1] = points[k];
      const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, z1 - z0) / DRAPE_M));
      for (let i = 1; i <= n; i++) flat.push([x0 + (x1 - x0) * i / n, z0 + (z1 - z0) * i / n]);
    }
    const n = flat.length, pos = new Float32Array(n * 6), uv = new Float32Array(n * 4), index = [], along = [0];
    let y = player.position.y;
    for (let i = 0; i < n; i++) {
      const [x, z] = flat[i];
      const [px, pz] = flat[Math.max(0, i - 1)], [nx, nz] = flat[Math.min(n - 1, i + 1)];
      let dx = nx - px, dz = nz - pz; const l = Math.hypot(dx, dz) || 1; dx /= l; dz /= l;
      if (i) along.push(along[i - 1] + Math.hypot(x - flat[i - 1][0], z - flat[i - 1][1]));
      const g = world.groundAt(x, z, y + 8); if (g !== null) y = g;
      // the two edges, half the width either side across the direction of travel
      const hx = -dz * WIDTH / 2, hz = dx * WIDTH / 2;
      pos.set([x + hx, y + LIFT, z + hz, x - hx, y + LIFT, z - hz], i * 6);
      const v = along[i] / CHEVRON_M; uv.set([0, v, 1, v], i * 4);
      if (i) index.push(2 * i - 2, 2 * i - 1, 2 * i, 2 * i - 1, 2 * i + 1, 2 * i);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    geo.setIndex(index);
    geo.computeBoundingSphere();
    return { geo, along };
  }

  function build() {
    if (mesh) { scene.remove(mesh); mesh.geometry.dispose(); mesh = null; }
    if (!nav) { app.invalidate(); return; }
    const { geo, along } = ribbon(nav.line.pts);
    nav.along = along;
    mesh = new THREE.Mesh(geo, material); mesh.name = 'route-ribbon'; mesh.renderOrder = 3;
    scene.add(mesh); trim(); app.invalidate();
  }

  // hide the ribbon the walker has already passed
  function trim() {
    if (!mesh || !nav.along) return;
    let i = 0; while (i < nav.along.length - 1 && nav.along[i + 1] < nav.s - 1) i++;
    const start = i * 6, count = Math.max(0, (nav.along.length - 1 - i) * 6);
    if (mesh.geometry.drawRange.start !== start) { mesh.geometry.setDrawRange(start, count); app.invalidate(); }
  }

  app.on('route', r => {
    if (!r) { nav = null; hud.hidden = true; build(); return; }
    const line = polyline(r.route.points);
    nav = { line, turns: turns(line), place: r.place, stepFree: r.stepFree, s: 0, seg: 0, along: null };
    arrived = false; offSince = 0; hud.hidden = false; hud.classList.remove('arrived');
    build(); update(performance.now(), true);
  });
  app.on('tile', () => { if (nav) build(); });

  const _dir = new THREE.Vector3();
  function update(now, force = false) {
    if (!nav) return;
    const from = player.guide ?? player.position;
    const p = progress(nav.line, from.x, from.z, nav.seg, nav.s);
    nav.s = p.s; nav.seg = p.seg;
    trim();
    const left = Math.max(0, nav.line.length - nav.s);
    // arrival is the walker near the entrance itself, not a short route left from a point off to the side
    if (!arrived && Math.hypot(from.x - nav.line.pts.at(-1)[0], from.z - nav.line.pts.at(-1)[1]) < ARRIVE_M) {
      arrived = true; hud.classList.add('arrived');
      stepEl.textContent = `You have arrived at ${nav.place.name}`; leftEl.textContent = 'Entrance nearby';
      app.toast(`You have arrived at ${nav.place.name}.`);
      return;
    }
    if (arrived) return;
    // off the route for a while: route again from here
    const slack = OFF_M + (app.follow?.accuracy ?? 0);
    if (p.off > slack) {
      offSince ||= now;
      if (now - offSince > OFF_S * 1000) { offSince = 0; app.route?.go(nav.place, { stepFree: nav.stepFree }); return; }
    } else offSince = 0;
    if (!force && now - lastUi < UI_MS) return;
    lastUi = now;
    const next = nextStep(nav.line, nav.turns, nav.s, nav.place.name);
    const [tx, tz] = pointAt(nav.line, nav.s + AHEAD_M);
    camera.getWorldDirection(_dir);
    const view = (Math.atan2(_dir.x, -_dir.z) * 180 / Math.PI + 360) % 360;
    arrow.style.transform = `rotate(${arrowAngle(from.x, from.z, tx, tz, view).toFixed(0)}deg)`;
    stepEl.textContent = next.inM < 8 ? next.text : `${next.text} in ${roundDistance(next.inM)}`;
    leftEl.textContent = `${roundDistance(left)} · ${walkMinutes(left)} min`;
  }

  app.on('frame', ({ time }) => { if (nav && app.state.mode === 'walk') update(time); });

  return { get active() { return !!nav; } };
}

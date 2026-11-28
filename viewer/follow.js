// Follow me: the phone's GPS position and compass drive the walk camera.
// The position never leaves the device: nothing here stores, logs or sends it.
import * as THREE from 'three';
import { CAMPUS, convergenceDeg, latLonToLocal, formatDistance } from './geo.js';
import { DECLINATION, phoneView, compassOf, easeAngle, angleDiff, yawForBearing, createTrack, campusCheck } from './follow-math.js';

const CONV = convergenceDeg(CAMPUS.lat, CAMPUS.lon);
const WEAK_M = 80;        // a fix less accurate than this is not used
const OFFSET_RATE = 0.5;  // per second: how fast an iOS compass offset settles
const PRIVACY = 'Your location stays on this device. It is not stored or sent.';

/** Builds the "Use my location" button for walk mode. Returns { start, stop, get active }. */
export function createFollow(app) {
  const { player, scene } = app;
  const overlay = document.getElementById('overlay');
  const box = document.createElement('div'); box.className = 'follow'; box.hidden = true;
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'follow-btn'; button.setAttribute('aria-pressed', 'false');
  button.title = PRIVACY;
  button.innerHTML = '<span class="follow-main">Use my location</span><span class="follow-note">Stays on this device</span>';
  const info = document.createElement('span'); info.className = 'follow-info'; info.setAttribute('aria-live', 'polite');
  box.append(button, info); overlay.append(box);
  const label = button.querySelector('.follow-main'), note = button.querySelector('.follow-note');

  // the accuracy circle on the ground around the walker
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.92, 1, 64).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ color: '#2f80ed', transparent: true, opacity: 0.55, depthWrite: false }),
  );
  ring.name = 'follow-accuracy'; ring.visible = false; ring.renderOrder = 2; scene.add(ring);

  const track = createTrack();
  let active = false, starting = false, shown = false, gen = 0, moveSeq = -1, watch = null, placing = false, placed = false, accuracy = 0;
  let heading = null, pitch = null, wantHeading = null, wantPitch = 0, offset = null, lastOrient = 0;
  const orientEvent = 'ondeviceorientationabsolute' in window ? 'deviceorientationabsolute' : 'deviceorientation';

  const say = text => { info.textContent = text; };

  function onOrient(e) {
    if (e.alpha === null || e.beta === null) return;
    const view = phoneView(e.alpha, e.beta ?? 0, e.gamma ?? 0);
    const compass = compassOf(e);
    let magnetic;
    if (e.absolute && typeof e.webkitCompassHeading !== 'number') magnetic = view.heading; // alpha already measured from north
    else if (compass !== null) {
      // iOS: alpha starts anywhere; webkitCompassHeading says where north is. Learn the offset between them,
      // only where the phone is clearly flat or clearly held up so both name the same edge.
      const clear = view.flat ? Math.abs(view.pitch) > 64 : Math.abs(view.pitch) < 37;
      const d = angleDiff(view.heading, compass);
      if (offset === null) offset = d;
      else if (clear) offset += angleDiff(offset, d) * Math.min(1, OFFSET_RATE * Math.max(0.016, (e.timeStamp - lastOrient) / 1000));
      magnetic = view.heading + offset;
    } else return; // a relative event with no compass cannot say where north is
    lastOrient = e.timeStamp;
    wantHeading = magnetic + DECLINATION;
    wantPitch = Math.max(-60, Math.min(45, view.pitch));
    player.guide && (player.guide.look = false);
  }

  function onFix(p) {
    if (!active) return;
    const { latitude, longitude, accuracy: acc } = p.coords;
    const { x, z } = latLonToLocal(latitude, longitude);
    const b = app.bounds;
    const where = campusCheck(x, z, { x0: b.min.x, x1: b.max.x, z0: b.min.z, z1: b.max.z });
    if (!where.on) {
      say(`You are ${formatDistance(where.distance)} from the campus`);
      if (!placed) app.toast(`You are ${formatDistance(where.distance)} from the campus. Your place in the model stays where it is.`);
      return;
    }
    if (acc > WEAK_M) { say(`Weak GPS signal (±${Math.round(acc)} m). Waiting for a better fix.`); return; }
    accuracy = acc;
    const s = track.add(p.timestamp / 1000, x, z, acc);
    say(`±${Math.round(acc)} m`);
    if (!placed && !placing) place(s.x, s.z);
  }

  /** The lowest surface at (x, z): a person with a phone is on the ground or the ground floor, not on a roof. */
  function lowestAt(x, z) {
    let y = app.world.groundAt(x, z), low = y;
    for (let i = 0; i < 8 && y !== null; i++) { y = app.world.groundAt(x, z, y - 0.3); if (y !== null) low = y; }
    return low;
  }

  async function place(x, z) {
    const my = gen;
    placing = true; shown = true; // the camera moves to the user's position from here on
    try {
      let move = player.teleport(x, z); moveSeq = player.moveSeq;
      let ok = await move;
      if (my !== gen) return;
      const low = ok ? lowestAt(x, z) : null;
      if (low !== null && low < player.position.y - 1) { move = player.teleport(x, z, low); moveSeq = player.moveSeq; ok = await move; }
      if (my !== gen) return;
      if (ok) { placed = true; player.guide = { x, z, look: wantHeading === null }; }
      else if (ok === false) say('No ground in the model here yet');
    } finally { if (my === gen) placing = false; }
  }

  function onError(err) {
    const text = err.code === 1 ? 'Location is off for this site. Turn it on in the browser settings to follow you.'
      : err.code === 3 ? 'No GPS fix yet. Try outside, away from tall walls.' : 'Your location is not available.';
    say(text); app.toast(text);
    if (err.code === 1) stop();
  }

  async function start() {
    if (active || starting) return;
    if (!('geolocation' in navigator)) { app.toast('This browser cannot read your location.'); return; }
    const my = ++gen; starting = true;
    try {
      // iOS asks for motion access only from a tap, so this comes before anything else awaits
      const ask = window.DeviceOrientationEvent?.requestPermission;
      if (typeof ask === 'function') {
        try { if (await ask.call(DeviceOrientationEvent) !== 'granted') app.toast('Without motion access the view will not turn with your phone. Drag to look around.'); }
        catch { /* not from a tap, or refused */ }
      }
    } finally { starting = false; }
    // the user may have left walk mode or tapped stop while the prompt was open
    if (my !== gen || app.state.mode !== 'walk') return;
    active = true; placed = false; track.reset(); heading = pitch = wantHeading = offset = null;
    button.setAttribute('aria-pressed', 'true'); button.classList.add('on');
    label.textContent = 'Following you'; note.textContent = 'Tap to stop';
    say('Finding you…');
    addEventListener(orientEvent, onOrient);
    watch = navigator.geolocation.watchPosition(onFix, onError, { enableHighAccuracy: true, maximumAge: 1000, timeout: 20000 });
  }

  function stop() {
    gen++;
    if (placing) { player.cancelMove(moveSeq); placing = false; }
    if (watch !== null) navigator.geolocation.clearWatch(watch);
    watch = null; active = false; placed = false; track.reset();
    removeEventListener(orientEvent, onOrient);
    player.guide = null; ring.visible = false;
    button.setAttribute('aria-pressed', 'false'); button.classList.remove('on');
    label.textContent = 'Use my location'; note.textContent = 'Stays on this device';
    say(''); app.invalidate();
  }

  button.onclick = () => (active || starting ? stop() : start());
  // a move to a place, the overview or a share link takes the view away from the user's position
  app.on('fly', () => { if (!active) shown = false; });
  // sit under the header, whose height changes with the screen width (it wraps on a phone)
  function placeBox() {
    const bottom = document.getElementById('top')?.getBoundingClientRect().bottom ?? 0;
    box.style.top = `${Math.round(Math.max(0, bottom)) + 8}px`;
  }
  app.on('resize', placeBox);
  app.on('mode', ({ mode }) => { box.hidden = mode !== 'walk'; placeBox(); if (mode !== 'walk' && (active || starting)) stop(); });

  app.on('frame', ({ dt }) => {
    if (!active || !placed || !player.guide) return;
    const s = track.state();
    if (s) { player.guide.x = s.x; player.guide.z = s.z; }
    if (wantHeading !== null) {
      heading = easeAngle(heading, wantHeading, dt);
      pitch = pitch === null ? wantPitch : pitch + (wantPitch - pitch) * (1 - Math.exp(-dt * 8));
      player.yaw = yawForBearing(heading, CONV);
      player.pitch = THREE.MathUtils.degToRad(pitch);
    }
    const pos = player.position;
    ring.position.set(pos.x, pos.y + 0.04, pos.z);
    ring.scale.setScalar(Math.max(1, accuracy));
    ring.visible = true;
  });

  return {
    start, stop, get active() { return active; },
    /** True from the first fix until the view moves to a place (a `fly` event): until then the view shows where the user is. */
    get private() { return active || shown; },
    /** Metres, the last fix's accuracy (0 when off). */
    get accuracy() { return active ? accuracy : 0; },
  };
}

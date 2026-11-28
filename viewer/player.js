// Fly and walk movement. Reads one intent per frame from viewer/input.js and moves the camera.
// Walking: a capsule slides along walls, a ground ray follows the surface, steps up curbs and stairs,
// and refuses to step where the model has no ground (the model is a work in progress and has gaps).
import * as THREE from 'three';
import { limitVelocity } from './flight-math.js';

const EYE = 1.65, RADIUS = 0.3, STEP = 0.5, HEIGHT = 1.75;
const WALK = 2.8, RUN = 7, GRAVITY = 16, JUMP = 5.6, SUBSTEP = 0.2;
const DOWN = new THREE.Vector3(0, -1, 0);
const sleep = ms => new Promise(r => setTimeout(r, ms));

export function createPlayer(app) {
  const { camera, scene, world } = app;
  const position = new THREE.Vector3(), vel = new THREE.Vector3(), flyVel = new THREE.Vector3();
  let yaw = 0, pitch = 0, grounded = false, eyeY = 0, busy = false, flySpeed = 40, stride = 0, seq = 0;
  let placed = false; // true once a teleport has put the walker on the ground; until then `position` is stale
  const going = new THREE.Vector3(); // where a teleport in progress is heading
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const avatar = new THREE.Group(); avatar.name = 'avatar'; avatar.visible = false;
  {
    const coat = new THREE.MeshStandardMaterial({ color: '#b3282d', roughness: 0.6 });
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.26, 0.95, 4, 12), coat); body.position.y = 0.78;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), new THREE.MeshStandardMaterial({ color: '#e8c9a8', roughness: 0.8 })); head.position.y = 1.6;
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.18, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), coat); cap.position.y = 1.63;
    const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.02, 12), coat); brim.position.set(0, 1.64, -0.2);
    for (const m of [body, head, cap, brim]) { m.castShadow = true; avatar.add(m); }
  }
  scene.add(avatar);

  const fwd = new THREE.Vector3(), right = new THREE.Vector3(), look = new THREE.Vector3();
  const _a = new THREE.Vector3(), _b = new THREE.Vector3(), _o = new THREE.Vector3(), _out = new THREE.Vector3(), _next = new THREE.Vector3(), _want = new THREE.Vector3();
  const status = text => app.emit('player:status', { text });

  function basis() {
    fwd.set(-Math.sin(yaw), 0, -Math.cos(yaw)); right.set(-fwd.z, 0, fwd.x);
    look.set(Math.cos(pitch) * fwd.x, Math.sin(pitch), Math.cos(pitch) * fwd.z);
  }
  /** Take yaw and pitch from wherever the camera points now. */
  function lookFromCamera() {
    camera.getWorldDirection(_a);
    yaw = Math.atan2(-_a.x, -_a.z); pitch = Math.asin(THREE.MathUtils.clamp(_a.y, -1, 1));
  }
  function turn(intent) {
    yaw -= intent.lookX; pitch = THREE.MathUtils.clamp(pitch + intent.lookY, -1.45, 1.45);
  }

  function fly(dt, intent) {
    if (intent.zoom) { flySpeed = THREE.MathUtils.clamp(flySpeed * Math.pow(1.12, intent.zoom), 2, 400); app.emit('player:speed', { speed: flySpeed }); }
    _want.set(0, 0, 0).addScaledVector(look, intent.moveZ).addScaledVector(right, intent.moveX);
    _want.y += intent.rise;
    if (_want.lengthSq() > 1) _want.normalize();
    _want.multiplyScalar(flySpeed * (intent.run ? 3 : 1));
    flyVel.lerp(_want, 1 - Math.exp(-dt * 8)); // ease in and out instead of stopping dead
    if (flyVel.lengthSq() < 1e-4) flyVel.set(0, 0, 0);
    // the soft flight limit: the outward part slows over its last stretch; sliding along it and coming back are free
    if (app.limit) Object.assign(flyVel, limitVelocity(camera.position, flyVel, app.limit));
    camera.position.addScaledVector(flyVel, dt);
    camera.lookAt(_a.copy(camera.position).add(look));
  }

  function tryStep(dx, dz) {
    _next.set(position.x + dx, position.y, position.z + dz);
    _a.set(_next.x, _next.y + STEP + RADIUS, _next.z); _b.set(_next.x, _next.y + HEIGHT - RADIUS, _next.z);
    _out.set(0, 0, 0);
    if (world.pushOut(_a, _b, RADIUS, _out)) { _next.x += _out.x; _next.z += _out.z; }
    const hit = world.raycast(_o.set(_next.x, _next.y + STEP, _next.z), DOWN, STEP + 60);
    if (!hit) return !grounded && (position.copy(_next), true); // never walk off the model; mid-air keeps drifting
    if (grounded) {
      const g = hit.point.y;
      if (g > _next.y + 0.02 && hit.normal.y < 0.45) return false; // too steep to climb
      if (g >= _next.y - 0.6) _next.y = g; else grounded = false;  // follow the ground, or step off a ledge
    }
    position.copy(_next); return true;
  }

  function walk(dt, intent) {
    if (busy) return;
    const speed = intent.run ? RUN : WALK;
    _want.set(0, 0, 0).addScaledVector(fwd, intent.moveZ).addScaledVector(right, intent.moveX).multiplyScalar(speed);
    const k = 1 - Math.exp(-dt * (grounded ? 12 : 3));
    vel.x += (_want.x - vel.x) * k; vel.z += (_want.z - vel.z) * k;
    if (intent.jump && grounded) { vel.y = JUMP; grounded = false; }
    const dx = vel.x * dt, dz = vel.z * dt, d = Math.hypot(dx, dz);
    if (d > 1e-5) {
      const n = Math.ceil(d / SUBSTEP);
      for (let i = 0; i < n; i++) if (!tryStep(dx / n, dz / n)) { vel.x = vel.z = 0; break; }
      if (grounded) stride += d;
    }
    if (!grounded) {
      const y0 = position.y;
      vel.y -= GRAVITY * dt; position.y += vel.y * dt;
      // sweep the whole fall since the last frame, so a slow frame cannot carry the feet through a landing
      const top = Math.max(y0, position.y);
      const hit = vel.y <= 0 && world.raycast(_o.set(position.x, top + STEP, position.z), DOWN, top - position.y + STEP + 0.05);
      if (hit) { position.y = hit.point.y; vel.y = 0; grounded = true; }
      if (position.y < app.bounds.min.y - 60) respawn();
    }
    place(dt);
  }

  function place(dt) {
    // smooth the eye over stairs and curbs; follow exactly in the air
    const target = position.y + EYE;
    eyeY = grounded && dt > 0 ? eyeY + (target - eyeY) * (1 - Math.exp(-dt * 16)) : target;
    if (Math.abs(target - eyeY) > 1.2) eyeY = target;
    if (app.state.view === 'first') {
      const bob = calm || !grounded ? 0 : Math.sin(stride * 4.2) * 0.022 * Math.min(1, Math.hypot(vel.x, vel.z) / WALK);
      camera.position.set(position.x, eyeY + bob, position.z);
      camera.lookAt(_a.copy(camera.position).add(look));
    } else {
      // the avatar casts a shadow: when it moves, the shadow map must follow (look.js redraws it only on request)
      if (avatar.visible && (!avatar.position.equals(position) || avatar.rotation.y !== yaw)) app.look.invalidateShadows();
      avatar.position.copy(position); avatar.rotation.y = yaw;
      const head = _a.set(position.x, eyeY - 0.15, position.z);
      let back = 4.5;
      const hit = world.raycast(head, _b.copy(look).negate(), back + 0.3, { builtOnly: true });
      if (hit) back = Math.max(0.8, hit.distance - 0.3); // keep the camera out of walls
      camera.position.copy(head).addScaledVector(look, -back);
      camera.lookAt(head);
    }
  }

  /**
   * Put the player on the ground at (x, z). Waits for the tile there and prepares collision first.
   * `y` picks a storey: the surface at or just below that height.
   * Resolves true on arrival, false if there is nothing to stand on, null if something else cancelled it.
   */
  async function teleport(x, z, y = null) {
    const my = ++seq; busy = true; going.set(x, y ?? 0, z);
    const cancelled = () => my !== seq || app.state.mode !== 'walk';
    try {
      if (!world.isLoaded(x, z)) {
        status('Loading this part of the campus…'); world.prioritize(x, z);
        while (!world.isLoaded(x, z)) { await sleep(150); if (cancelled()) return null; }
      }
      status('Preparing the ground…');
      await world.warm(x, z, 45);
      if (cancelled()) return null;
      const g = world.groundAt(x, z, y === null ? null : y + 1.2);
      if (g === null) { status('Nothing to stand on there. Try a spot on the campus.'); return false; }
      position.set(x, g + 0.02, z); vel.set(0, 0, 0); grounded = true; eyeY = position.y + EYE; placed = true;
      basis(); place(0); app.invalidate();
      status('');
      return true;
    } finally { if (my === seq) busy = false; }
  }

  /** Back to the middle of the campus. */
  async function respawn() {
    const c = app.bounds.getCenter(new THREE.Vector3());
    const start = app.home ?? c;
    for (const [dx, dz] of [[0, 0], [12, 0], [-12, 0], [0, 12], [0, -12], [30, 30], [-30, -30]]) {
      const ok = await teleport(start.x + dx, start.z + dz);
      if (ok !== false) return ok; // arrived, or cancelled
    }
    return false;
  }

  function step(dt, intent) {
    turn(intent); basis();
    if (app.state.mode === 'fly') fly(dt, intent); else walk(dt, intent);
  }

  return {
    position, step, teleport, respawn, lookFromCamera,
    jump() { if (grounded && !busy) { vel.y = JUMP; grounded = false; } },
    stop() { vel.set(0, 0, 0); flyVel.set(0, 0, 0); seq++; busy = false; placed = false; status(''); },
    refresh() { basis(); if (app.state.mode === 'walk') place(0); },
    get yaw() { return yaw; }, set yaw(v) { yaw = v; },
    get pitch() { return pitch; }, set pitch(v) { pitch = v; },
    get grounded() { return grounded; }, get busy() { return busy; },
    /** False from a mode change until the walker stands on the ground: `position` is not valid yet. */
    get placed() { return placed; },
    /** The point tiles should load around: the destination while a teleport waits for it, else the feet. */
    get focus() { return busy ? going : position; },
    get flySpeed() { return flySpeed; }, set flySpeed(v) { flySpeed = v; },
    get moving() { return vel.lengthSq() > 1e-4 || flyVel.lengthSq() > 1e-4 || !grounded && app.state.mode === 'walk' && !busy; },
    avatar,
  };
}

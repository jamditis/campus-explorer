// Eased camera moves in orbit mode. A move ends early when the user touches the view.
import * as THREE from 'three';

const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export function createCamera(app) {
  const { camera, controls, canvas } = app;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let move = null;
  const p0 = new THREE.Vector3(), t0 = new THREE.Vector3(), p = new THREE.Vector3(), t = new THREE.Vector3();

  function finish(done) {
    if (!move) return;
    const m = move; move = null; m.resolve(done);
  }
  // any direct manipulation of the view cancels the move
  for (const type of ['pointerdown', 'wheel', 'touchstart']) canvas.addEventListener(type, () => finish(false), { passive: true });

  /**
   * Glide to a pose. `pose` = { position: Vector3, target: Vector3 }. Options: `duration` seconds,
   * `lift` extra height at the middle of the move as a fraction of the distance travelled.
   * Resolves true when it arrives and false when the user interrupts.
   */
  function flyTo(pose, { duration = 1.6, lift = 0.12 } = {}) {
    finish(false);
    if (app.state.mode !== 'orbit') app.setMode('orbit');
    if (calm || duration <= 0) {
      camera.position.copy(pose.position); controls.target.copy(pose.target); controls.update(); app.invalidate();
      return Promise.resolve(true);
    }
    p0.copy(camera.position); t0.copy(controls.target);
    return new Promise(resolve => {
      move = { pose: { position: pose.position.clone(), target: pose.target.clone() }, t: 0, duration, arc: p0.distanceTo(pose.position) * lift, resolve };
    });
  }

  app.on('frame', ({ dt }) => {
    if (!move) return;
    move.t = Math.min(1, move.t + dt / move.duration);
    const k = ease(move.t);
    p.lerpVectors(p0, move.pose.position, k); p.y += Math.sin(Math.PI * k) * move.arc;
    t.lerpVectors(t0, move.pose.target, k);
    camera.position.copy(p); controls.target.copy(t); camera.lookAt(t);
    if (move.t >= 1) { controls.update(); finish(true); }
  });

  return { flyTo, cancel: () => finish(false), get busy() { return !!move; } };
}

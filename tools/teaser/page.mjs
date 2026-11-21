// In-page helpers for the teaser capture: pose a shot, and wait until the viewer has drawn it and
// nothing is pending. Everything here runs on the viewer page through Playwright, at capture time only;
// the viewer's own files are not changed.

/** Install window.__teaser on a viewer page opened with ?capture (window.__campus must exist). */
export async function installSettle(page) {
  await page.evaluate(() => {
    const c = window.__campus, app = c.app, look = app.look;
    // capture draws are never "moving": full resolution (no governor) and a fresh cull each frame
    const render = look.render.bind(look), update = look.update.bind(look);
    // Draws are real only when asked for (t.live): while the viewer settles (grass scattered over many
    // frames, trees and far versions swapped, textures arriving) its frames run without drawing, so a
    // software renderer that needs half a minute per draw draws each captured frame once.
    look.render = () => { if (t.live) { render(false); t.live = false; t.real++; pending = false; } };
    // Shadows: the viewer moves its shadow box with the view and redraws the shadow map when it moves.
    // A shot may instead name one box for the whole move (`t.shadow = { focus, half }`): the map is then
    // drawn once and again only when the sun or the graphics change, and its texels do not crawl.
    const sun = look.sun, sc = sun.shadow.camera, d = new c.THREE.Vector3();
    let key = '', pending = false;
    look.update = (target) => {
      update(target, true);
      const s = t.shadow;
      if (!s || !sun.castShadow) { key = ''; return; }
      d.subVectors(sun.position, sun.target.position).normalize().multiplyScalar(2500);
      sc.left = sc.bottom = -s.half; sc.right = sc.top = s.half; sc.near = 10; sc.far = 6000; sc.updateProjectionMatrix();
      sun.target.position.set(...s.focus); sun.position.set(...s.focus).add(d);
      sun.target.updateMatrixWorld();
      const k = `${s.focus}|${s.half}|${d.x.toFixed(3)},${d.y.toFixed(3)},${d.z.toFixed(3)}|${t.version}`;
      if (k !== key) pending = true; // kept until a real draw has drawn the shadow map
      sun.shadow.needsUpdate = pending; key = k;
    };
    // orbit controls keep the camera a little above its target; a film camera may look up
    c.controls.maxPolarAngle = Math.PI * 0.97; c.controls.minDistance = 0.5;
    const t = window.__teaser = { draws: 0, real: 0, live: false, shadow: null, version: 0 };
    app.on('drawn', () => { t.draws++; });
    t.shot = ({ pose, fov = 50, time = null, shadow }) => {
      t.mark = t.draws;
      // a frame that repeats the last pose, lens, light and shadow box asks for no draw (still shots)
      const key = JSON.stringify([pose, fov, time, shadow, t.version]);
      t.same = key === t.lastKey;
      if (t.same) return;
      t.lastKey = key;
      if (shadow !== undefined) t.shadow = shadow;
      if (time) app.setTime(new Date(time));
      c.goto(...pose);
      c.camera.fov = fov; c.camera.updateProjectionMatrix();
      app.invalidate();
    };
    // resolves once the viewer has gone quiet since the last pose (no frame asked for a draw for `quiet`
    // animation frames), then draws one real frame
    t.settled = (from, quiet = 4) => new Promise(done => {
      let still = 0, seen = t.draws, phase = 0, real = 0, guard = 0;
      const tick = () => {
        guard++;
        if (phase === 0) {
          if (t.draws !== seen) { seen = t.draws; still = 0; } else still++;
          // nothing in the scene changed (a still shot; the interface may change): the canvas still holds this frame
          if (still >= quiet && (t.draws === from || t.same)) { done(0); return; }
          if (still >= quiet || guard > 3000) { phase = 1; real = t.real; t.live = true; app.invalidate(); }
        } else if (t.real > real) { done(t.draws - from); return; }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  });
}

/** Wait until the frame posed last has been drawn and the viewer has gone quiet. Returns the draw count. */
export async function settle(page, from = null) {
  return page.evaluate(f => window.__teaser.settled(f ?? window.__teaser.mark ?? 0), from);
}

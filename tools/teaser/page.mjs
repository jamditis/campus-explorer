// In-page helpers for the teaser capture: pose a shot, and wait until the viewer has drawn it and
// nothing is pending. Everything here runs on the viewer page through Playwright, at capture time only;
// the viewer's own files are not changed.

/** Install window.__teaser on a viewer page opened with ?capture (window.__campus must exist). */
export async function installSettle(page) {
  await page.evaluate(() => {
    const c = window.__campus, app = c.app, look = app.look;
    // capture draws are never "moving": full resolution (no governor) and a fresh cull each frame
    const render = look.render.bind(look), update = look.update.bind(look);
    look.render = () => render(false);
    // Shadows: the viewer moves its shadow box with the view and redraws the shadow map when it moves.
    // A shot may instead name one box for the whole move (`t.shadow = { focus, half }`): the map is then
    // drawn once and again only when the sun or the graphics change, and its texels do not crawl.
    const sun = look.sun, sc = sun.shadow.camera, d = new c.THREE.Vector3();
    let key = '';
    look.update = (target) => {
      update(target, true);
      const s = t.shadow;
      if (!s || !sun.castShadow) { key = ''; return; }
      d.subVectors(sun.position, sun.target.position).normalize().multiplyScalar(2500);
      sc.left = sc.bottom = -s.half; sc.right = sc.top = s.half; sc.near = 10; sc.far = 6000; sc.updateProjectionMatrix();
      sun.target.position.set(...s.focus); sun.position.set(...s.focus).add(d);
      sun.target.updateMatrixWorld();
      const k = `${s.focus}|${s.half}|${d.x.toFixed(3)},${d.y.toFixed(3)},${d.z.toFixed(3)}|${t.version}`;
      sun.shadow.needsUpdate = k !== key; key = k;
    };
    // orbit controls keep the camera a little above its target; a film camera may look up
    c.controls.maxPolarAngle = Math.PI * 0.97; c.controls.minDistance = 0.5;
    const t = window.__teaser = { draws: 0, shadow: null, version: 0 };
    app.on('drawn', () => { t.draws++; });
    t.shot = ({ pose, fov = 50, time = null, shadow }) => {
      t.mark = t.draws;
      if (shadow !== undefined) t.shadow = shadow;
      if (time) app.setTime(new Date(time));
      c.goto(...pose);
      c.camera.fov = fov; c.camera.updateProjectionMatrix();
      app.invalidate();
    };
    // resolves once a draw has happened since `from` and then `quiet` animation frames pass with no draw
    t.settled = (from, quiet = 3) => new Promise(done => {
      let still = 0, seen = t.draws;
      const tick = () => {
        if (t.draws !== seen) { seen = t.draws; still = 0; } else if (t.draws > from) still++;
        if (still >= quiet) done(t.draws - from); else requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  });
}

/** Wait until the frame posed last has been drawn and the viewer has gone quiet. Returns the draw count. */
export async function settle(page, from = null) {
  return page.evaluate(f => window.__teaser.settled(f ?? window.__teaser.mark ?? 0), from);
}

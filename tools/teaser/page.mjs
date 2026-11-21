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
    look.update = (target) => update(target, true);
    // orbit controls keep the camera a little above its target; a film camera may look up
    c.controls.maxPolarAngle = Math.PI * 0.97; c.controls.minDistance = 0.5;
    const t = window.__teaser = { draws: 0 };
    app.on('drawn', () => { t.draws++; });
    t.shot = ({ pose, fov = 50, time = null }) => {
      t.mark = t.draws;
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

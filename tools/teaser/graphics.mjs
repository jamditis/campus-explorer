// The teaser's 3D graphics: extruded letters, dimension lines and pins added to the viewer's scene at
// capture time only. `installGraphics` runs in the page (passed to page.evaluate), so it must not use
// anything from this module's scope; the pure placement maths it needs is passed in as source text.

/* global window */
export function installGraphics({ fonts, mathSource }) {
  const c = window.__campus, THREE = c.THREE, app = c.app, scene = app.scene;
  const M = new Function(`${mathSource}; return { dimension, wipeShaft, layout, stagger, ease, clamp01 };`)();
  const mats = {
    white: new THREE.MeshStandardMaterial({ color: '#f1eee7', roughness: 0.55, metalness: 0 }),
    red: new THREE.MeshStandardMaterial({ color: '#b3282d', roughness: 0.5, metalness: 0 }),
    ink: new THREE.MeshStandardMaterial({ color: '#2a2b2e', roughness: 0.7, metalness: 0 }),
  };
  const glyphGeo = new Map(); // `${font}|${ch}|${depth}` -> geometry (unit em size)
  function glyph(fontName, ch, depth, bevel) {
    const key = `${fontName}|${ch}|${depth}|${bevel}`;
    if (glyphGeo.has(key)) return glyphGeo.get(key);
    const g = fonts[fontName].glyphs[ch];
    let geo = null;
    if (g && g.shapes.length) {
      const shapes = g.shapes.map(s => {
        const sh = new THREE.Shape(s.outer.map(([x, y]) => new THREE.Vector2(x, y)));
        for (const h of s.holes) sh.holes.push(new THREE.Path(h.map(([x, y]) => new THREE.Vector2(x, y))));
        return sh;
      });
      geo = new THREE.ExtrudeGeometry(shapes, {
        depth, curveSegments: 1, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel * 0.6, bevelSegments: 2,
      });
      geo.computeVertexNormals();
    }
    glyphGeo.set(key, geo);
    return geo;
  }
  const items = new Map();
  const root = new THREE.Group(); root.name = 'teaser_graphics'; scene.add(root);
  const shade = o => { o.castShadow = true; o.receiveShadow = true; o.frustumCulled = false; };

  /**
   * Text: { id, text, font, size (m cap-ish em), depth (m), at [x,y,z], yaw, flat (lie on the ground,
   * reading from the south side unless yaw turns it), colour, tracking (em), rise: 'ground' | 'extrude' }
   */
  function addText(d) {
    const group = new THREE.Group(), font = fonts[d.font ?? 'semibold'];
    const { chars } = M.layout(d.text, font.glyphs, { tracking: d.tracking ?? 0, align: d.align ?? 'centre' });
    const depthEm = (d.depth ?? d.size * 0.18) / d.size, bevel = d.bevel ?? 0.012;
    const letters = [];
    for (const { ch, x } of chars) {
      const geo = glyph(d.font ?? 'semibold', ch, depthEm, bevel);
      if (!geo) continue;
      const pivot = new THREE.Group(); pivot.position.x = x;
      const m = new THREE.Mesh(geo, mats[d.colour ?? 'white']); shade(m);
      m.position.z = -depthEm / 2; pivot.add(m);
      group.add(pivot); letters.push(pivot);
    }
    group.scale.setScalar(d.size);
    const holder = new THREE.Group(); holder.add(group);
    holder.position.set(...d.at); holder.rotation.order = 'YXZ'; holder.rotation.y = d.yaw ?? 0;
    if (d.flat) holder.rotation.x = -Math.PI / 2;
    if (d.tilt) holder.rotation.x = d.tilt;
    root.add(holder);
    items.set(d.id, { d, kind: 'text', holder, group, letters });
  }

  /** Dimension line: { id, a, b, head, tick, up, width (m), label (text item id placed at mid) } */
  function addDimension(d) {
    const dim = M.dimension(d.a, d.b, { head: d.head ?? 3, tick: d.tick ?? 2, up: d.up ?? [0, 1, 0] });
    const w = d.width ?? 0.5, mat = mats[d.colour ?? 'white'];
    const bar = (p, q) => {
      const g = new THREE.BoxGeometry(1, 1, 1), m = new THREE.Mesh(g, mat); shade(m);
      m.userData.set = (P, Q) => {
        const a = new THREE.Vector3(...P), b = new THREE.Vector3(...Q), L = a.distanceTo(b);
        m.visible = L > 0.01; if (!m.visible) return;
        m.position.copy(a).add(b).multiplyScalar(0.5);
        m.quaternion.setFromUnitVectors(new THREE.Vector3(1, 0, 0), b.clone().sub(a).normalize());
        // the bar's thin side faces along `side x dir`, its flat side in the line's plane
        m.scale.set(L, w, w);
      };
      m.userData.set(p, q); return m;
    };
    const holder = new THREE.Group(); root.add(holder);
    const shaft = bar(...dim.shaft); holder.add(shaft);
    const ticks = dim.ticks.map(t => { const m = bar(...t); holder.add(m); return m; });
    const heads = dim.heads.map(([tip, l, r]) => {
      const g = new THREE.BufferGeometry();
      // a flat triangle with thickness: two faces and the rim, as a small extruded prism
      const T = new THREE.Vector3(...tip), L = new THREE.Vector3(...l), R = new THREE.Vector3(...r);
      const n = new THREE.Vector3().subVectors(L, T).cross(new THREE.Vector3().subVectors(R, T)).normalize().multiplyScalar(w / 2);
      const P = [T, L, R].flatMap(p => [p.clone().add(n), p.clone().sub(n)]);
      const idx = [0, 2, 4, 1, 5, 3, 0, 1, 3, 0, 3, 2, 2, 3, 5, 2, 5, 4, 4, 5, 1, 4, 1, 0];
      g.setAttribute('position', new THREE.Float32BufferAttribute(P.flatMap(p => [p.x, p.y, p.z]), 3));
      g.setIndex(idx); g.computeVertexNormals();
      const m = new THREE.Mesh(g, mats[d.headColour ?? d.colour ?? 'white']); shade(m); holder.add(m);
      m.userData.tip = T; return m;
    });
    items.set(d.id, { d, kind: 'dim', holder, dim, shaft, ticks, heads });
  }

  /** Pin: a thin post from the ground with a ball at the top. { id, at [x,y,z] (foot), height, radius } */
  function addPin(d) {
    const holder = new THREE.Group(); holder.position.set(...d.at); root.add(holder);
    const r = d.radius ?? 0.25;
    const post = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 10).translate(0, 0.5, 0), mats.white); shade(post);
    const ball = new THREE.Mesh(new THREE.SphereGeometry(r * 4, 20, 14), mats[d.colour ?? 'red']); shade(ball);
    holder.add(post, ball);
    items.set(d.id, { d, kind: 'pin', holder, post, ball });
  }

  /** Pose every graphic for a time in the shot: states { id: { on, raw, up, down } } from path.presence. */
  function pose(states) {
    for (const [id, it] of items) {
      const s = states[id];
      it.holder.visible = !!s && s.raw > 0;
      if (!it.holder.visible) continue;
      const d = it.d;
      if (it.kind === 'text') {
        const n = it.letters.length;
        it.letters.forEach((l, i) => {
          const u = s.up < 1 ? M.stagger(s.up, i, n, d.spread ?? 0.45) : 1;
          const k = (s.up < 1 ? M.ease.back(u) : 1) * (s.down < 1 ? M.ease.smooth(s.down) : 1);
          if ((d.rise ?? 'ground') === 'ground') {
            // rise out of the ground (or roof): the letter starts below its base line, hidden by what it stands on
            l.position.y = -(1 - k) * 1.1; l.scale.set(1, 1, 1); l.visible = k > 0.001 || s.down >= 1;
          } else {
            // extrude: grow out of the surface it lies on, with a slight scale-in
            l.scale.set(0.85 + 0.15 * k, 0.85 + 0.15 * k, Math.max(0.001, k)); l.position.y = 0; l.visible = k > 0.001;
          }
        });
      } else if (it.kind === 'dim') {
        const w = M.ease.smoother(s.up) * (s.down < 1 ? M.ease.smooth(s.down) : 1);
        it.shaft.userData.set(...M.wipeShaft(it.dim.shaft, w));
        const tw = M.clamp01((w - 0.85) / 0.15);
        it.heads.forEach(h => { h.visible = w > 0.6; h.scale.setScalar(1); });
        // heads ride the shaft ends out to the tips
        it.heads.forEach((h, i) => {
          const tip = it.dim.heads[i][0], end = i ? it.dim.shaft[1] : it.dim.shaft[0];
          const mid = it.dim.mid, k = w;
          const want = mid.map((v, j) => v + (tip[j] - v) * k);
          h.position.set(want[0] - tip[0], want[1] - tip[1], want[2] - tip[2]);
          void end;
        });
        it.ticks.forEach((t, i) => {
          const [p, q] = it.dim.ticks[i], m = p.map((v, j) => (v + q[j]) / 2);
          t.userData.set(m.map((v, j) => v + (p[j] - v) * tw), m.map((v, j) => v + (q[j] - v) * tw));
        });
      } else if (it.kind === 'pin') {
        const k = M.ease.back(s.up) * (s.down < 1 ? M.ease.smooth(s.down) : 1), h = d.height ?? 12;
        it.post.scale.set(1, Math.max(0.001, h * Math.min(1, k)), 1);
        it.ball.position.y = h * Math.min(1, k) ; it.ball.scale.setScalar(Math.max(0.001, k));
      }
    }
    // the shadow map is drawn again only when a graphic moved (see page.mjs)
    const sig = [...items.keys()].map(id => (states[id] ? `${states[id].up.toFixed(4)},${states[id].down.toFixed(4)}` : '-')).join('|');
    if (sig !== lastSig) { lastSig = sig; window.__teaser.version++; app.look.invalidateShadows(); }
    app.invalidate();
  }
  let lastSig = '';
  function clear() { for (const it of items.values()) root.remove(it.holder); items.clear(); lastSig = ''; window.__teaser.version++; }
  window.__teaser.graphics = { addText, addDimension, addPin, pose, clear, items };
}

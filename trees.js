// Tree LOD: per-instance culling for instanced trees, two middle versions, and cheap impostors past a
// quality-set distance. Every instanced tree group (crown + trunk meshes sharing a parent and instance list) keeps
// its original matrices; each update writes the instances that are in view to the full meshes (near), to one of
// two middle versions (TREE_MID, TREE_FAR_MID: the same buffers with the thinnest bark left out, see
// viewer/treelod-math.js) or, out to FAR, to one shared low-poly crown impostor (per-instance size and colour).
// Trees that are plain meshes (a tree used once in a tile, or joined copies) get the same middle versions through
// their draw range. Shrub leaf-card batches draw one card in SHRUB_THIN, grown, past SHRUB_REACH.
import * as THREE from 'three';
import { farCells, standIn, STAND_IN } from './viewer/trees-math.js';
import {
  barkOrder, reorderIndex, thinPick, scaleLinear, treeBand,
  TREE_MID, TREE_FAR_MID, BARK_MIN_DIAMETER, BARK_SHARE, SHRUB_REACH, SHRUB_THIN,
} from './viewer/treelod-math.js';

const DIST = { low: 220, medium: 420, high: 700 };
const FAR = 2600;
const CACHE = 64; // reordered bark indices kept for meshes that recur across tiles at the same scale

/**
 * @param onChange called when work done in idle time changed what is drawn (middle versions became ready)
 */
export function createTrees(scene, camera, onChange = () => {}) {
  let groups = [], plains = [], shrubs = [], last = 0;
  let dist = DIST.medium, mid = TREE_MID.medium, farMid = TREE_FAR_MID.medium, reach = SHRUB_REACH.medium;
  const cap = 30000;
  const geo = new THREE.IcosahedronGeometry(1, 1);
  geo.translate(0, 0.15, 0);
  const imp = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ roughness: 0.95, flatShading: false, envMapIntensity: 0.25 }), cap);
  imp.count = 0; imp.frustumCulled = false; imp.castShadow = true; imp.receiveShadow = true; imp.name = 'tree_impostors';
  imp.setColorAt(0, new THREE.Color()); scene.add(imp);
  const trunkGeo = new THREE.CylinderGeometry(0.5, 0.7, 1, 5, 1, true); trunkGeo.translate(0, 0.5, 0);
  const trunks = new THREE.InstancedMesh(trunkGeo, new THREE.MeshStandardMaterial({ color: '#4a3d33', roughness: 1 }), cap);
  trunks.count = 0; trunks.frustumCulled = false; trunks.castShadow = false; trunks.name = 'tree_impostor_trunks'; scene.add(trunks);

  const avgCanvas = document.createElement('canvas'); avgCanvas.width = avgCanvas.height = 16;
  const avgCtx = avgCanvas.getContext('2d', { willReadFrequently: true });
  const avgCache = new WeakMap(); // by image, so a tile dropped from memory does not keep its leaf textures alive
  // mean colour of a leaf texture's opaque pixels, times the material colour
  function leafColour(m) {
    const c = m.color.clone();
    const img = m.map?.image;
    if (!img) return c.multiplyScalar(0.6);
    if (!avgCache.has(img)) {
      let r = 0, g = 0, b = 0, n = 0;
      try {
        avgCtx.clearRect(0, 0, 16, 16); avgCtx.drawImage(img, 0, 0, 16, 16);
        const d = avgCtx.getImageData(0, 0, 16, 16).data;
        for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 128) { r += d[i]; g += d[i + 1]; b += d[i + 2]; n++; }
      } catch { /* unreadable image: fall back to material colour */ }
      avgCache.set(img, n ? new THREE.Color().setRGB(r / n / 255, g / n / 255, b / n / 255, THREE.SRGBColorSpace) : new THREE.Color(0.25, 0.35, 0.18));
    }
    // a little darker: the impostor has no gaps between leaves for shadow to show through
    return c.multiply(avgCache.get(img)).multiplyScalar(0.8);
  }

  function add(root) {
    root.updateMatrixWorld(true);
    const byKey = new Map();
    root.traverse(o => {
      if (!o.isInstancedMesh || o.count < 2 || o.userData.treeLod) return;
      const k = o.parent.uuid + ':' + o.count;
      if (!byKey.has(k)) byKey.set(k, []);
      byKey.get(k).push(o);
    });
    const m4 = new THREE.Matrix4(), p = new THREE.Vector3(), s = new THREE.Vector3(), q = new THREE.Quaternion(), rec = new Float32Array(STAND_IN);
    for (const list of byKey.values()) {
      // whole trees only: a group needs leaf crowns AND a trunk/branch mesh; instanced shrub leaf cards
      // (Leaf_Shrub_*, one card per instance) stay outside the tree LOD
      const crowns = list.filter(o => [].concat(o.material)[0]?.userData.leaf);
      if (!crowns.length || crowns.length === list.length || list.some(o => /shrub/i.test(o.name))) continue;
      const a = list[0], n = a.count;
      // local crown box (all leaf meshes) and full tree box, in instance space
      const cb = new THREE.Box3(), tb = new THREE.Box3();
      for (const o of list) {
        if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
        tb.union(o.geometry.boundingBox);
        if (crowns.includes(o)) cb.union(o.geometry.boundingBox);
      }
      const col = leafColour([].concat(crowns[0].material)[0]);
      const pos = new Float32Array(n * 3), rad = new Float32Array(n), imps = [], mats = list.map(o => o.instanceMatrix.array.slice());
      const cc = cb.getCenter(new THREE.Vector3()), cs = cb.getSize(new THREE.Vector3());
      let smax = 0; // the largest instance scale: no instance loses a branch thicker than BARK_MIN_DIAMETER
      for (let i = 0; i < n; i++) {
        a.getMatrixAt(i, m4); m4.premultiply(a.matrixWorld);
        p.copy(cc).applyMatrix4(m4); pos.set([p.x, p.y, p.z], i * 3);
        m4.decompose(new THREE.Vector3(), q, s);
        smax = Math.max(smax, Math.abs(s.x), Math.abs(s.y), Math.abs(s.z));
        const base = new THREE.Vector3(cc.x, tb.min.y, cc.z).applyMatrix4(m4);
        rec.set([p.x, p.y, p.z, cs.x * s.x / 2, cs.y * s.y / 2, cs.z * s.z / 2, base.x, base.y, base.z, (tb.max.y - tb.min.y) * s.y / 2, col.r, col.g, col.b]);
        const t = toImp(standIn(rec)); rad[i] = t.rad; imps.push(t);
      }
      for (const o of list) { o.userData.treeLod = true; o.frustumCulled = false; }
      const g = { list, n, pos, rad, mats, imps, col, mids: null };
      groups.push(g);
      // the middle versions are built in idle time; until then the full meshes draw in their place
      later(() => { if (groups.includes(g)) g.mids = middles(list, smax); });
    }
    root.traverse(o => {
      if (!o.isMesh || o.userData.treeLod) return;
      const m = [].concat(o.material)[0];
      if (o.isInstancedMesh) {
        if (o.count >= 2 && m?.userData.leaf && /shrub/i.test(o.name) && tris(o.geometry) <= 4) shrubs.push(thinned(o));
        return;
      }
      // a plain tree's bark (a tree used once in its tile, or copies joined into one mesh)
      if (!/^Tree_/.test(o.name) || m?.userData.leaf || !o.geometry.index) return;
      if (!o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
      const scale = o.matrixWorld.getMaxScaleOnAxis();
      const t = { o, c: o.geometry.boundingSphere.center.clone().applyMatrix4(o.matrixWorld), r: o.geometry.boundingSphere.radius * scale, kept: null };
      plains.push(t);
      later(() => {
        if (!plains.includes(t)) return;
        t.kept = ordered(o.geometry, scale);
        o.geometry.boundsTree = null; // collision: a BVH built on the old triangle order is built again when a ray needs it
      });
    });
    update(true);
  }

  const tris = geo => (geo.index ? geo.index.count : geo.attributes.position.count) / 3;
  // Reorder a bark geometry's triangles for its middle versions (viewer/treelod-math.js), once per geometry; the
  // same mesh in another tile (same counts, same first vertex, same scale) reuses the reordered index.
  const cache = new Map();
  function ordered(geo, scale) {
    if (geo.userData.barkKept) return geo.userData.barkKept;
    const pos = geo.attributes.position, idx = geo.index;
    let kept = [tris(geo), tris(geo)];
    if (pos && idx && pos.count) {
      const key = `${idx.count}:${pos.count}:${pos.getX(0)}:${pos.getY(0)}:${pos.getZ(0)}:${scale.toFixed(2)}`;
      let hit = cache.get(key);
      if (!hit) {
        // as the GPU sees them: quantized (normalized, often interleaved) positions read back as floats
        const a = new Float32Array(pos.count * 3);
        for (let i = 0; i < pos.count; i++) { a[i * 3] = pos.getX(i); a[i * 3 + 1] = pos.getY(i); a[i * 3 + 2] = pos.getZ(i); }
        const r = barkOrder(a, idx.array, { minDiameter: BARK_MIN_DIAMETER, scale, shares: [BARK_SHARE.near, BARK_SHARE.far] });
        hit = { index: reorderIndex(idx.array, r.order), kept: r.kept };
        cache.set(key, hit);
        if (cache.size > CACHE) cache.delete(cache.keys().next().value);
      }
      idx.array.set(hit.index); idx.needsUpdate = true; // in place: the same GPU buffer, now in the new order
      kept = hit.kept;
    }
    geo.userData.barkKept = kept;
    return kept;
  }
  // The two middle versions of an instanced tree group: for each of its meshes an instanced mesh beside it on the
  // same geometry buffers, the bark drawn over a shorter range, the leaves whole.
  function middles(list, smax) {
    return [0, 1].map(b => list.map(o => {
      const leaf = [].concat(o.material)[0]?.userData.leaf;
      let geo = o.geometry;
      if (!leaf) {
        const kept = ordered(o.geometry, smax * o.matrixWorld.getMaxScaleOnAxis());
        geo = new THREE.BufferGeometry();
        for (const [k, v] of Object.entries(o.geometry.attributes)) geo.setAttribute(k, v);
        geo.setIndex(o.geometry.index); geo.setDrawRange(0, kept[b] * 3);
        geo.boundingBox = o.geometry.boundingBox; geo.boundingSphere = o.geometry.boundingSphere;
      }
      const m = new THREE.InstancedMesh(geo, o.material, o.instanceMatrix.count);
      m.name = `${o.name}_mid${b + 1}`; m.count = 0; m.visible = false; m.frustumCulled = false;
      m.castShadow = o.castShadow; m.receiveShadow = o.receiveShadow;
      m.position.copy(o.position); m.quaternion.copy(o.quaternion); m.scale.copy(o.scale);
      m.userData.treeLod = true;
      o.parent.add(m); m.updateMatrixWorld(true);
      return m;
    }));
  }
  // A shrub leaf-card batch and its thinned stand-in: one card in SHRUB_THIN, each grown by sqrt(SHRUB_THIN).
  function thinned(o) {
    const pick = thinPick(o.count, SHRUB_THIN), f = Math.sqrt(SHRUB_THIN);
    const t = new THREE.InstancedMesh(o.geometry, o.material, pick.length);
    const src = o.instanceMatrix.array, dst = t.instanceMatrix.array;
    pick.forEach((i, k) => { dst.set(src.subarray(i * 16, i * 16 + 16), k * 16); scaleLinear(dst, k * 16, f); });
    t.name = `${o.name}_thin`; t.castShadow = o.castShadow; t.receiveShadow = o.receiveShadow; t.visible = false;
    t.position.copy(o.position); t.quaternion.copy(o.quaternion); t.scale.copy(o.scale);
    t.userData.treeLod = true;
    o.parent.add(t); t.updateMatrixWorld(true); t.computeBoundingSphere();
    o.userData.treeLod = true; // out of look.js's size culling: drawn, thinned or hidden here
    o.computeBoundingBox();
    return { o, t, box: o.boundingBox.clone().applyMatrix4(o.matrixWorld) };
  }

  // work for idle time, a piece per slice; the view is refreshed once the queue is empty
  const queue = []; let pumping = false;
  const idle = fn => (globalThis.requestIdleCallback ? requestIdleCallback(fn, { timeout: 1000 }) : setTimeout(() => fn(null), 16));
  function later(fn) { queue.push(fn); if (!pumping) { pumping = true; idle(pump); } }
  function pump(deadline) {
    const t0 = performance.now();
    // at least one piece per call: a busy page gives idle callbacks no time left once their timeout passes
    if (queue.length) do queue.shift()();
    while (queue.length &&(deadline ? deadline.timeRemaining() > 2 : performance.now() - t0 < 8));
    if (queue.length) { idle(pump); return; }
    pumping = false; update(true); onChange();
  }

  const toImp = t => ({ c: new THREE.Vector3(...t.c), s: new THREE.Vector3(...t.s), base: new THREE.Vector3(...t.base), trunkH: t.trunkH, trunkW: t.trunkW, rad: t.rad, col: new THREE.Color(...t.col) });
  // Stand-ins for the instanced trees of a tile that is not in memory (lite profile), from its far version's
  // `trees` records (viewer/trees-math.js STAND_IN): drawn as impostors at any distance while `on`.
  const ghosts = new Map();
  function addPoints(key, a, on) {
    const trees = []; for (let i = 0; i < Math.floor(a.length / STAND_IN); i++) trees.push(toImp(standIn(a, i)));
    ghosts.set(key, { trees, on }); update(true);
  }
  function showPoints(key, on) { const g = ghosts.get(key); if (g && g.on !== on) { g.on = on; update(true); } }
  const frustum = new THREE.Frustum(), pv = new THREE.Matrix4(), sph = new THREE.Sphere(), v = new THREE.Vector3();
  const im4 = new THREE.Matrix4(), one = new THREE.Quaternion();
  function update(force) {
    const now = performance.now(); if (!force && now - last < 250) return; last = now;
    camera.updateMatrixWorld(); pv.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse); frustum.setFromProjectionMatrix(pv);
    const cp = camera.position; let ni = 0, nt = 0;
    for (const g of groups) {
      const k = [0, 0, 0], lists = g.mids ? [g.list, ...g.mids] : [g.list];
      for (let i = 0; i < g.n; i++) {
        sph.center.set(g.pos[i * 3], g.pos[i * 3 + 1], g.pos[i * 3 + 2]); sph.radius = g.rad[i] * 1.3;
        const d = sph.center.distanceTo(cp);
        if (d > FAR || !frustum.intersectsSphere(sph)) continue;
        const band = treeBand(d, mid, farMid, dist);
        if (band < 3) {
          const b = g.mids ? band : 0, list = lists[b];
          for (let j = 0; j < list.length; j++) list[j].instanceMatrix.array.set(g.mats[j].subarray(i * 16, i * 16 + 16), k[b] * 16);
          k[b]++;
        } else if (ni < cap) {
          const t = g.imps[i];
          im4.compose(t.c, one, t.s); imp.setMatrixAt(ni, im4); imp.setColorAt(ni, g.col); ni++;
          if (d < dist * 2.5 && nt < cap) { im4.compose(v.copy(t.base), one, v.clone().set(t.trunkW, t.trunkH, t.trunkW)); trunks.setMatrixAt(nt++, im4); }
        }
      }
      lists.forEach((list, b) => { for (const o of list) { o.count = k[b]; o.instanceMatrix.needsUpdate = true; o.visible = k[b] > 0; } });
    }
    for (const gh of ghosts.values()) {
      if (!gh.on) continue;
      for (const t of gh.trees) {
        sph.center.copy(t.c); sph.radius = t.rad * 1.3;
        const d = sph.center.distanceTo(cp);
        if (d > FAR || ni >= cap || !frustum.intersectsSphere(sph)) continue;
        im4.compose(t.c, one, t.s); imp.setMatrixAt(ni, im4); imp.setColorAt(ni, t.col); ni++;
        if (d < dist * 2.5 && nt < cap) { im4.compose(v.copy(t.base), one, v.clone().set(t.trunkW, t.trunkH, t.trunkW)); trunks.setMatrixAt(nt++, im4); }
      }
    }
    for (const t of plains) {
      if (!t.kept) continue;
      const band = treeBand(Math.max(0, t.c.distanceTo(cp) - t.r), mid, farMid, Infinity);
      t.o.geometry.setDrawRange(0, band ? t.kept[band - 1] * 3 : Infinity);
    }
    for (const sh of shrubs) {
      const d = sh.box.distanceToPoint(cp);
      sh.o.visible = d < reach; sh.t.visible = d >= reach && d < FAR;
    }
    imp.count = ni; trunks.count = nt;
    imp.instanceMatrix.needsUpdate = true; if (imp.instanceColor) imp.instanceColor.needsUpdate = true; trunks.instanceMatrix.needsUpdate = true;
  }
  // far-field trees from land cover: [x, y, z, crown radius, height] in three.js axes, always impostors.
  // One instanced mesh per FAR_CELL ground cell (trees-math.js), each with its own bounding sphere, so the
  // frustum skips the cells out of view in the view and in the shadow map (one mesh for all drew them all).
  const farGeo = new THREE.IcosahedronGeometry(1, 0); farGeo.translate(0, 0.1, 0);
  const farMat = new THREE.MeshStandardMaterial({ roughness: 1, envMapIntensity: 0.2 });
  let far = null;
  function addFar(a) {
    if (far) { scene.remove(far); for (const o of far.children) o.dispose(); }
    far = new THREE.Group(); far.name = 'far_trees_cells';
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), p = new THREE.Vector3(), s = new THREE.Vector3(), c = new THREE.Color();
    const up = new THREE.Vector3(0, 1, 0);
    const tones = ['#3f5530', '#4a603a', '#556a36', '#3d4b33', '#5a6e3e', '#64753f'].map(h => new THREE.Color(h));
    for (const [key, ids] of farCells(a)) {
      const mesh = new THREE.InstancedMesh(farGeo, farMat, ids.length);
      mesh.name = 'far_trees'; mesh.userData.cell = key; mesh.castShadow = true; mesh.receiveShadow = true;
      ids.forEach((i, k) => {
        const x = a[i * 5], y = a[i * 5 + 1], z = a[i * 5 + 2], r = a[i * 5 + 3], h = a[i * 5 + 4];
        q.setFromAxisAngle(up, (i * 2.399) % 6.283);
        p.set(x, y + h - r * 1.1, z); s.set(r, r * 1.15, r);
        m4.compose(p, q, s); mesh.setMatrixAt(k, m4);
        c.copy(tones[i % tones.length]).multiplyScalar(0.85 + ((i * 7919) % 100) / 330); mesh.setColorAt(k, c);
      });
      mesh.computeBoundingSphere();
      far.add(mesh);
    }
    scene.add(far);
  }
  /** Draw every tree in full, whatever the camera sees (for a picture from another camera). `update(true)` undoes it. */
  function showAll() {
    for (const g of groups) {
      g.list.forEach((o, j) => { o.instanceMatrix.array.set(g.mats[j]); o.count = g.n; o.instanceMatrix.needsUpdate = true; o.visible = true; });
      for (const list of g.mids || []) for (const o of list) { o.count = 0; o.visible = false; }
    }
    // the stand-ins of tiles not in memory, all of them (no culling for another camera)
    let ni = 0;
    for (const gh of ghosts.values()) if (gh.on) for (const t of gh.trees) {
      if (ni >= cap) break;
      im4.compose(t.c, one, t.s); imp.setMatrixAt(ni, im4); imp.setColorAt(ni, t.col); ni++;
    }
    imp.count = ni; trunks.count = 0; imp.instanceMatrix.needsUpdate = true; if (imp.instanceColor) imp.instanceColor.needsUpdate = true;
  }
  /** Forget the trees of a tile that was dropped from memory. */
  function remove(root) {
    const under = o => { for (let p = o; p; p = p.parent) if (p === root) return true; return false; };
    const n = groups.length; groups = groups.filter(g => !under(g.list[0]));
    plains = plains.filter(t => !under(t.o)); shrubs = shrubs.filter(sh => !under(sh.o));
    if (groups.length !== n) update(true);
  }
  /**
   * Lower trees whose trunk base hangs over the ground. `gapAt(base, group)` returns how far the base is above
   * the ground under it, or 0 to leave the tree alone. Returns how many trees moved.
   */
  function settle(gapAt) {
    const sc = new THREE.Vector3(); let moved = 0;
    for (const g of groups) {
      const sy = sc.setFromMatrixScale(g.list[0].matrixWorld).y || 1;
      for (let i = 0; i < g.n; i++) {
        const t = g.imps[i], gap = gapAt(t.base, g);
        if (!(gap > 0)) continue;
        for (const m of g.mats) m[i * 16 + 13] -= gap / sy; // the instance's own translation, in the mesh's space
        g.pos[i * 3 + 1] -= gap; t.c.y -= gap; t.base.y -= gap; moved++;
      }
    }
    if (moved) update(true);
    return moved;
  }
  function setQuality(name) {
    const q = DIST[name] ? name : 'medium';
    dist = DIST[q]; mid = TREE_MID[q]; farMid = TREE_FAR_MID[q]; reach = SHRUB_REACH[q];
    update(true);
  }
  function reset() {
    groups = []; plains = []; shrubs = []; ghosts.clear(); queue.length = 0; imp.count = 0; trunks.count = 0;
  }
  return {
    add, remove, settle, showAll, addFar, addPoints, showPoints, update, setQuality, reset,
    /** Trees drawn per version, plain trees drawn as a middle version, shrub batches thinned, idle work left. */
    get stats() {
      const n = (g, b) => (b === 0 ? g.list : g.mids?.[b - 1])?.[0].count ?? 0;
      return {
        groups: groups.length, impostors: imp.count, pending: queue.length,
        full: groups.reduce((a, g) => a + n(g, 0), 0),
        middle: groups.reduce((a, g) => a + n(g, 1), 0), farMiddle: groups.reduce((a, g) => a + n(g, 2), 0),
        plainMiddle: plains.filter(t => t.kept && t.o.geometry.drawRange.count !== Infinity).length,
        shrubsThinned: shrubs.filter(sh => sh.t.visible).length,
      };
    },
  };
}

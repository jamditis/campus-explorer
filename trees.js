// Tree LOD: per-instance culling for instanced trees, with cheap impostors past a quality-set distance.
// Every instanced tree group (crown + trunk meshes sharing a parent and instance list) keeps its
// original matrices; each update writes only the instances that are near and in view, and the
// rest become one shared low-poly crown impostor (per-instance size and colour) out to FAR.
import * as THREE from 'three';

const DIST = { low: 220, medium: 420, high: 700 };
const FAR = 2600;

export function createTrees(scene, camera) {
  let groups = [], dist = DIST.medium, last = 0;
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
  const avgCache = new Map();
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
    const m4 = new THREE.Matrix4(), p = new THREE.Vector3(), s = new THREE.Vector3(), q = new THREE.Quaternion();
    for (const list of byKey.values()) {
      const crowns = list.filter(o => [].concat(o.material)[0]?.userData.leaf);
      if (!crowns.length) continue;
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
      for (let i = 0; i < n; i++) {
        a.getMatrixAt(i, m4); m4.premultiply(a.matrixWorld);
        p.copy(cc).applyMatrix4(m4); pos.set([p.x, p.y, p.z], i * 3);
        m4.decompose(new THREE.Vector3(), q, s);
        const sx = cs.x * s.x / 2, sy = cs.y * s.y / 2, sz = cs.z * s.z / 2;
        rad[i] = Math.max(sx, sy, sz, (tb.max.y - tb.min.y) * s.y / 2);
        const base = new THREE.Vector3(cc.x, tb.min.y, cc.z).applyMatrix4(m4);
        imps.push({ c: p.clone(), s: new THREE.Vector3(sx * 0.95, sy * 0.95, sz * 0.95), base, trunkH: Math.max(0.5, p.y - sy * 0.6 - base.y), trunkW: Math.max(0.12, Math.min(sx, sz) * 0.08) });
      }
      for (const o of list) { o.userData.treeLod = true; o.frustumCulled = false; }
      groups.push({ list, n, pos, rad, mats, imps, col });
    }
    update(true);
  }

  const frustum = new THREE.Frustum(), pv = new THREE.Matrix4(), sph = new THREE.Sphere(), v = new THREE.Vector3();
  const im4 = new THREE.Matrix4(), one = new THREE.Quaternion();
  function update(force) {
    const now = performance.now(); if (!force && now - last < 250) return; last = now;
    camera.updateMatrixWorld(); pv.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse); frustum.setFromProjectionMatrix(pv);
    const cp = camera.position; let ni = 0, nt = 0;
    for (const g of groups) {
      let k = 0;
      for (let i = 0; i < g.n; i++) {
        sph.center.set(g.pos[i * 3], g.pos[i * 3 + 1], g.pos[i * 3 + 2]); sph.radius = g.rad[i] * 1.3;
        const d = sph.center.distanceTo(cp);
        if (d > FAR || !frustum.intersectsSphere(sph)) continue;
        if (d < dist) {
          for (let j = 0; j < g.list.length; j++) g.list[j].instanceMatrix.array.set(g.mats[j].subarray(i * 16, i * 16 + 16), k * 16);
          k++;
        } else if (ni < cap) {
          const t = g.imps[i];
          im4.compose(t.c, one, t.s); imp.setMatrixAt(ni, im4); imp.setColorAt(ni, g.col); ni++;
          if (d < dist * 2.5 && nt < cap) { im4.compose(v.copy(t.base), one, v.clone().set(t.trunkW, t.trunkH, t.trunkW)); trunks.setMatrixAt(nt++, im4); }
        }
      }
      for (const o of g.list) { o.count = k; o.instanceMatrix.needsUpdate = true; o.visible = k > 0; }
    }
    imp.count = ni; trunks.count = nt;
    imp.instanceMatrix.needsUpdate = true; if (imp.instanceColor) imp.instanceColor.needsUpdate = true; trunks.instanceMatrix.needsUpdate = true;
  }
  // far-field trees from land cover: [x, y, z, crown radius, height] in three.js axes, always impostors
  const farGeo = new THREE.IcosahedronGeometry(1, 0); farGeo.translate(0, 0.1, 0);
  let far = null;
  function addFar(a) {
    if (far) { scene.remove(far); far.dispose(); }
    const n = Math.floor(a.length / 5);
    far = new THREE.InstancedMesh(farGeo, new THREE.MeshStandardMaterial({ roughness: 1, envMapIntensity: 0.2 }), n);
    far.name = 'far_trees'; far.castShadow = true; far.receiveShadow = true;
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), p = new THREE.Vector3(), s = new THREE.Vector3(), c = new THREE.Color();
    const tones = ['#2c3b20', '#34452a', '#3b4a26', '#2a3424', '#40502c', '#46532e'].map(h => new THREE.Color(h));
    for (let i = 0; i < n; i++) {
      const x = a[i * 5], y = a[i * 5 + 1], z = a[i * 5 + 2], r = a[i * 5 + 3], h = a[i * 5 + 4];
      q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), (i * 2.399) % 6.283);
      p.set(x, y + h - r * 1.1, z); s.set(r, r * 1.15, r);
      m4.compose(p, q, s); far.setMatrixAt(i, m4);
      c.copy(tones[i % tones.length]).multiplyScalar(0.85 + ((i * 7919) % 100) / 330); far.setColorAt(i, c);
    }
    far.computeBoundingSphere();
    scene.add(far);
  }
  function setQuality(name) { dist = DIST[name] || DIST.medium; update(true); }
  function reset() {
    groups = []; imp.count = 0; trunks.count = 0;
  }
  return { add, addFar, update, setQuality, reset, get stats() { return { groups: groups.length, impostors: imp.count }; } };
}

// Look and performance layer for the campus viewer: sky + image-based light, a sun that can be
// moved to any real position, shadows redrawn only when they change, ACES filmic tone mapping, fog,
// ambient occlusion, world-space CC0 textures per material category, painted lot markings,
// screen-size culling (cheap LOD), adaptive resolution and the quality levels.
import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// metres per texture repeat, and how strongly the texture modulates the model's own colour
const CATS = {
  asphalt: { file: 'asphalt', size: 3.5, k: 0.8 },
  concrete: { file: 'concrete', size: 2.5, k: 0.7 },
  brick: { file: 'brick', size: 2.2, k: 0.9 },
  plaster: { file: 'plaster', size: 3, k: 0.6 },
  rooftile: { file: 'rooftile', size: 2, k: 0.9 },
  pavers: { file: 'pavers', size: 2, k: 0.85 },
  grass: { file: 'grass', size: 2.4, k: 0.9 },
  mulch: { file: 'mulch', size: 1.6, k: 0.9 },
  gravel: { file: 'gravel', size: 1.5, k: 0.8 },
  stone: { file: 'stone', size: 1.8, k: 0.6 },
  metal: { file: 'metal', size: 1, k: 0.35 },
  wood: { file: 'wood', size: 1.2, k: 0.7 },
};
const ROUGH = { asphalt: 0.92, concrete: 0.85, brick: 0.88, plaster: 0.9, rooftile: 0.75, pavers: 0.85, grass: 1, mulch: 1, gravel: 0.95, stone: 0.7, metal: 0.45, wood: 0.8 };

export const QUALITY = {
  low: { pixelRatio: 1, shadows: 0, ao: false, cull: 0.02, tex: true, macro: false },
  medium: { pixelRatio: 1.5, shadows: 2048, ao: false, cull: 0.008, tex: true, macro: true },
  high: { pixelRatio: 2, shadows: 4096, ao: true, cull: 0.003, tex: true, macro: true },
};
const MIN_SCALE = 0.5; // lowest resolution scale the governor may use while the view moves
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const FILLER = /^(WS62_crown_|MID_street_trunk|Icosphere\.?001$)/; // far-field filler; glTF names drop the dot
const CROWN = new THREE.MeshStandardMaterial({ color: '#6b6a3c', roughness: .95 });

export function createLook(renderer, scene, camera) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.8;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // --- sky and sun. setSun() moves the sun; the caller supplies a real solar position ---
  const sky = new Sky(); sky.scale.setScalar(18000); sky.material.fog = false;
  const u = sky.material.uniforms;
  u.turbidity.value = 3.2; u.rayleigh.value = 1.1; u.mieCoefficient.value = 0.004; u.mieDirectionalG.value = 0.82;
  const sunDir = new THREE.Vector3(0, 1, 0);
  scene.add(sky);
  const DAY_FOG = new THREE.Color('#c6d4e1'), DUSK_FOG = new THREE.Color('#dcb9a0'), NIGHT_FOG = new THREE.Color('#0b101c');
  const HORIZON = DAY_FOG.clone();
  scene.fog = new THREE.FogExp2(HORIZON, 0.00016);
  scene.background = HORIZON;

  // image-based light from the same sky (gives glass and metal something to reflect)
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene(); const envSky = new Sky(); envSky.scale.setScalar(1000);
  Object.assign(envSky.material.uniforms, THREE.UniformsUtils.clone(u));
  envScene.add(envSky);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(900, 32).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: '#5d6247' }));
  ground.position.y = -5; envScene.add(ground);
  let envTarget = null; const envDir = new THREE.Vector3();
  function bakeEnvironment() {
    envSky.material.uniforms.sunPosition.value.copy(sunDir);
    const next = pmrem.fromScene(envScene, 0.02);
    scene.environment = next.texture; envTarget?.dispose(); envTarget = next; envDir.copy(sunDir);
  }
  scene.environmentIntensity = 0.3;

  const SKY_DAY = new THREE.Color('#dfe9f5'), SKY_NIGHT = new THREE.Color('#33415f');
  const SOIL_DAY = new THREE.Color('#4f4a3a'), SOIL_NIGHT = new THREE.Color('#12151c');
  const SUN_HIGH = new THREE.Color('#fff0dc'), SUN_LOW = new THREE.Color('#ff9a4d');
  const hemi = new THREE.HemisphereLight(SKY_DAY, SOIL_DAY, 0.2); scene.add(hemi);
  const sun = new THREE.DirectionalLight(SUN_HIGH, 2.7);
  sun.shadow.bias = -0.0002; sun.shadow.normalBias = 0.04;
  sun.shadow.autoUpdate = false; // the scene is static: redraw the shadow map only when something changed
  scene.add(sun, sun.target);
  let shadowDirty = true, elevation = 38, night = 0;

  /**
   * Point the sun. `dir` is a unit vector toward the sun in viewer space; `elevationDeg` its height above
   * the horizon. Below the horizon the sun light is off and a dim sky light keeps the model readable.
   */
  function setSun(dir, elevationDeg) {
    sunDir.copy(dir).normalize(); elevation = elevationDeg;
    u.sunPosition.value.copy(sunDir);
    const day = smooth(-5, 8, elevation), low = 1 - smooth(2, 25, elevation);
    night = 1 - smooth(-8, 0, elevation);
    sun.intensity = 2.7 * smooth(-1.5, 10, elevation);
    sun.color.copy(SUN_HIGH).lerp(SUN_LOW, low * 0.85);
    hemi.color.copy(SKY_NIGHT).lerp(SKY_DAY, day); hemi.groundColor.copy(SOIL_NIGHT).lerp(SOIL_DAY, day);
    hemi.intensity = 0.2 + 0.5 * (1 - day);
    HORIZON.copy(NIGHT_FOG).lerp(DAY_FOG, day).lerp(DUSK_FOG, low * day * 0.6);
    if (!envTarget || envDir.angleTo(sunDir) > 0.03) bakeEnvironment();
    glow.visible = night > 0.02; glowMat.opacity = night;
    applyShadows(); shadowDirty = true;
  }

  // --- lamps glow after dark: one additive sprite per lamp instance, no real lights ---
  const glowTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    r.addColorStop(0, 'rgba(255,236,190,1)'); r.addColorStop(0.25, 'rgba(255,214,140,.55)'); r.addColorStop(1, 'rgba(255,190,90,0)');
    g.fillStyle = r; g.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const glowMat = new THREE.PointsMaterial({ map: glowTex, size: 5, sizeAttenuation: true, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, toneMapped: false });
  const glow = new THREE.Points(new THREE.BufferGeometry(), glowMat); glow.frustumCulled = false; glow.visible = false; glow.name = 'lamp_glow'; scene.add(glow);
  let lampPoints = [];
  function addLamps(root) {
    const m = new THREE.Matrix4(), p = new THREE.Vector3(); let n = 0;
    root.traverse(o => {
      if (!o.isInstancedMesh || !/^Lamp_/i.test(o.name)) return;
      const bb = o.geometry.boundingBox ?? (o.geometry.computeBoundingBox(), o.geometry.boundingBox);
      for (let i = 0; i < o.count; i++) {
        o.getMatrixAt(i, m); m.premultiply(o.matrixWorld);
        p.set((bb.min.x + bb.max.x) / 2, bb.max.y - (bb.max.y - bb.min.y) * 0.08, (bb.min.z + bb.max.z) / 2).applyMatrix4(m);
        lampPoints.push(p.x, p.y, p.z); n++;
      }
    });
    if (n) glow.geometry.setAttribute('position', new THREE.Float32BufferAttribute(lampPoints, 3));
  }

  // --- post: AO (high quality only) ---
  let composer = null, gtao = null;
  function buildComposer() {
    composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    gtao = new GTAOPass(scene, camera, innerWidth, innerHeight);
    gtao.updateGtaoMaterial({ radius: 1.6, distanceExponent: 1.5, thickness: 2, scale: 1.1, samples: 12 });
    gtao.blendIntensity = 0.85;
    composer.addPass(gtao); composer.addPass(new OutputPass());
  }

  // --- textures per category ---
  const loader = new THREE.TextureLoader();
  const texCache = {};
  const texFor = c => texCache[c] ??= loader.load(`./textures/${CATS[c].file}.webp`, t => {
    t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.needsUpdate = true;
  });
  let paint = []; // [{tex, x0,x1,z0,z1}]
  const paintUniforms = { pMap: { value: [] }, pBox: { value: [] }, pN: { value: 0 } };
  const EMPTY = new THREE.DataTexture(new Uint8Array(4), 1, 1); EMPTY.needsUpdate = true;
  const paintTex = url => { const t = loader.load(url); t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  function setPaint(list, base) {
    paint = list.slice(0, 4).map(p => ({ ...p, tex: paintTex(base + p.file) }));
    const maps = [], boxes = [];
    for (let i = 0; i < 4; i++) {
      const p = paint[i];
      maps.push(p ? p.tex : EMPTY);
      // Blender (x, y) -> three (x, -z)
      boxes.push(p ? new THREE.Vector4(p.x0, -p.y1, p.x1 - p.x0, p.y1 - p.y0) : new THREE.Vector4(0, 0, 1, 1));
    }
    paintUniforms.pMap.value = maps; paintUniforms.pBox.value = boxes; paintUniforms.pN.value = paint.length;
  }
  let macroOn = true;
  const macroUniform = { value: 1 };

  function texturize(m, cat) {
    const def = CATS[cat]; if (!def || m.userData.tp) return;
    m.userData.tp = cat;
    if (ROUGH[cat] !== undefined && !m.roughnessMap) m.roughness = ROUGH[cat];
    if (cat !== 'metal') m.metalness = 0;
    const isAsphalt = cat === 'asphalt';
    m.onBeforeCompile = sh => {
      sh.uniforms.tpMap = { value: texFor(cat) };
      sh.uniforms.tpScale = { value: 1 / def.size };
      sh.uniforms.tpK = { value: def.k };
      sh.uniforms.tpMacro = macroUniform;
      if (isAsphalt) Object.assign(sh.uniforms, paintUniforms);
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vTpPos; varying vec3 vTpNrm;')
        .replace('#include <begin_vertex>', `#include <begin_vertex>
          vec4 tpW = vec4(transformed, 1.0);
          #ifdef USE_INSTANCING
            tpW = instanceMatrix * tpW;
          #endif
          vTpPos = (modelMatrix * tpW).xyz;
          vTpNrm = normalize(mat3(modelMatrix) * objectNormal);`);
      // objectNormal is declared by beginnormal_vertex, which runs before begin_vertex
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
          varying vec3 vTpPos; varying vec3 vTpNrm;
          uniform sampler2D tpMap; uniform float tpScale; uniform float tpK; uniform float tpMacro;
          ${isAsphalt ? 'uniform sampler2D pMap[4]; uniform vec4 pBox[4]; uniform int pN;' : ''}
          vec3 tpSample(vec3 p, vec3 w) {
            return texture2D(tpMap, p.zy).rgb * w.x + texture2D(tpMap, p.xz).rgb * w.y + texture2D(tpMap, p.xy).rgb * w.z;
          }`)
        .replace('#include <map_fragment>', `#include <map_fragment>
          {
            vec3 w = pow(abs(normalize(vTpNrm)), vec3(4.0)); w /= (w.x + w.y + w.z);
            vec3 t = tpSample(vTpPos * tpScale, w);
            if (tpMacro > 0.5) t = mix(t, tpSample(vTpPos * tpScale * 0.13 + 0.37, w), 0.35);
            t *= 2.7; // textures are normalised to a mid-grey mean (sRGB 160 ~ linear 0.37)
            diffuseColor.rgb *= mix(vec3(1.0), t, tpK);
            ${isAsphalt ? `
            for (int i = 0; i < 4; i++) {
              if (i >= pN) break;
              vec2 uv = (vTpPos.xz - pBox[i].xy) / pBox[i].zw;
              if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) continue;
              vec4 pc;
              if (i == 0) pc = texture2D(pMap[0], uv); else if (i == 1) pc = texture2D(pMap[1], uv);
              else if (i == 2) pc = texture2D(pMap[2], uv); else pc = texture2D(pMap[3], uv);
              diffuseColor.rgb = mix(diffuseColor.rgb, pc.rgb * mix(1.0, t.r, 0.25), pc.a);
            }` : ''}
          }`);
    };
    m.customProgramCacheKey = () => 'tp_' + cat;
    m.needsUpdate = true;
  }

  // --- per-mesh screen-size culling ---
  let items = [];
  const tmpS = new THREE.Sphere();
  function register(root) {
    root.updateMatrixWorld(true);
    root.traverse(o => {
      if (!o.isMesh || !o.visible) return;
      o.castShadow = true; o.receiveShadow = true;
      if (!o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
      if (o.isInstancedMesh) o.computeBoundingSphere();
      const bs = (o.isInstancedMesh ? o.boundingSphere : o.geometry.boundingSphere).clone().applyMatrix4(o.matrixWorld);
      if (bs.radius < 120) items.push({ o, c: bs.center, r: bs.radius });
      else o.visible = true;
      if (bs.radius > 400) o.castShadow = false; // far-field ground: receives only
    });
  }
  let cullK = QUALITY.medium.cull, lastCull = 0;
  function cull(force) {
    const now = performance.now(); if (!force && now - lastCull < 200) return; lastCull = now;
    const p = camera.position;
    for (const it of items) {
      const d = Math.max(1, p.distanceTo(it.c) - it.r);
      const v = it.r > d * cullK;
      if (v !== it.o.visible) { it.o.visible = v; if (it.r > 1.5) shadowDirty = true; } // tiny things do not move the shadow map
    }
  }

  let q = QUALITY.medium, qName = 'medium';
  function applyShadows() {
    const on = q.shadows > 0 && sun.intensity > 0.02;
    if (renderer.shadowMap.enabled !== on || sun.castShadow !== on) {
      renderer.shadowMap.enabled = on; sun.castShadow = on;
      scene.traverse(o => { if (o.material) for (const m of [].concat(o.material)) m.needsUpdate = true; });
    }
  }
  function applyQuality(name) {
    qName = name; q = QUALITY[name];
    scale = 1; applyScale(1);
    if (q.shadows) { sun.shadow.mapSize.set(q.shadows, q.shadows); sun.shadow.map?.dispose(); sun.shadow.map = null; }
    applyShadows(); shadowDirty = true;
    cullK = q.cull; macroUniform.value = q.macro ? 1 : 0;
    if (q.ao && !composer) buildComposer();
    scene.traverse(o => { if (o.material) for (const m of [].concat(o.material)) m.needsUpdate = true; });
    resize(); cull(true);
  }
  function resize() {
    const w = innerWidth, h = innerHeight;
    if (composer) { composer.setPixelRatio(renderer.getPixelRatio()); composer.setSize(w, h); }
  }

  // --- adaptive resolution: lower it while the view moves on a slow GPU, full resolution when still ---
  let scale = 1, applied = 1, ema = 16, slow = 0, fast = 0, lastDraw = 0, wasMoving = false;
  function applyScale(s) {
    applied = s;
    renderer.setPixelRatio(Math.min(devicePixelRatio, q.pixelRatio) * s);
    resize();
  }
  function govern(moving, now) {
    if (moving && wasMoving) {
      const ms = Math.min(250, now - lastDraw); ema = ema * 0.85 + ms * 0.15;
      if (ema > 34) { slow += ms; fast = 0; } else if (ema < 20) { fast += ms; slow = 0; } else slow = fast = 0;
      if (slow > 500 && scale > MIN_SCALE) { scale = Math.max(MIN_SCALE, scale * 0.8); slow = 0; }
      if (fast > 2500 && scale < 1) { scale = Math.min(1, scale * 1.15); fast = 0; }
    }
    wasMoving = moving; lastDraw = now;
    const want = moving ? scale : 1;
    if (want !== applied) applyScale(want);
  }

  const focus = new THREE.Vector3(), lastFocus = new THREE.Vector3(Infinity, 0, 0); let lastHalf = 0;
  /** Follow the view: shadow box, sky and culling. `settle` forces a cull (call it when the camera stops). */
  function update(target, settle = false) {
    // shadow box follows what you look at; sized to the view distance in steps, snapped to texels
    focus.copy(target ?? camera.position);
    const dist = camera.position.distanceTo(focus);
    const raw = THREE.MathUtils.clamp(dist * 0.9, 45, 700);
    const half = 45 * Math.pow(1.25, Math.round(Math.log(raw / 45) / Math.log(1.25)));
    const sc = sun.shadow.camera;
    if (sc.right !== half) { sc.left = -half; sc.right = half; sc.top = half; sc.bottom = -half; sc.near = 10; sc.far = 4000; sc.updateProjectionMatrix(); }
    const texel = (2 * half) / (q.shadows || 2048);
    focus.x = Math.round(focus.x / texel) * texel; focus.z = Math.round(focus.z / texel) * texel;
    focus.y = Math.round(focus.y / 4) * 4;
    if (half !== lastHalf || !focus.equals(lastFocus)) { lastHalf = half; lastFocus.copy(focus); shadowDirty = true; }
    sun.target.position.copy(focus); sun.position.copy(focus).addScaledVector(sunDir.y > 0.02 ? sunDir : _up, 1500);
    sky.position.copy(camera.position);
    cull(settle);
    if (shadowDirty && sun.castShadow) { sun.shadow.needsUpdate = true; shadowDirty = false; }
  }
  const _up = new THREE.Vector3(0, 1, 0);
  /** Draw one frame. `moving` tells the governor whether this is part of continuous motion. */
  function render(moving = false) {
    govern(moving, performance.now());
    if (q.ao && composer) composer.render(); else renderer.render(scene, camera);
  }
  /** Draw the scene with another camera into `target` without sky or fog (minimap, thumbnails). */
  function renderPlain(cam, target) {
    const fog = scene.fog, auto = sun.shadow.needsUpdate;
    scene.fog = null; sky.visible = false; glow.visible = false;
    renderer.setRenderTarget(target); renderer.render(scene, cam); renderer.setRenderTarget(null);
    scene.fog = fog; sky.visible = true; glow.visible = night > 0.02; sun.shadow.needsUpdate = auto;
  }
  function fixMaterials(root) {
    root.traverse(o => {
      if (!o.isMesh) return;
      if (root.name === 'context' && FILLER.test(o.name)) { o.visible = false; return; } // float above the exported skirt
      if (/^Icosphere/.test(o.name)) { o.material = CROWN; return; }
      for (const m of [].concat(o.material)) {
        if (!m) continue;
        if (m.map) m.map.anisotropy = 4;
        // leaf cards exported without an opacity map would show their white texture background: draw them as solid foliage
        if (/^Leaf_|needle/i.test(m.name) && !(m.alphaTest > 0) && !m.transparent) { m.map = null; m.color.set('#4f5a33'); m.side = THREE.DoubleSide; m.needsUpdate = true; continue; }
        if (m.alphaTest > 0 || (m.transparent && m.map)) { m.alphaTest = 0.45; m.transparent = false; m.side = THREE.DoubleSide; m.userData.leaf = true; }
        else if (m.transparent) { m.depthWrite = false; m.userData.glass = true; }
      }
    });
  }
  /** Prepare one loaded tile: material fixes, textures, culling registration, lamps. */
  function decorate(root) {
    fixMaterials(root);
    root.traverse(o => {
      if (!o.isMesh) return;
      for (const m of [].concat(o.material)) {
        if (!m) continue;
        const cat = m.userData?.cat;
        if ((m.userData?.glass || cat === 'glass') && !m.userData.glassDone) {
          m.userData.glassDone = true; // shared materials: tint once
          m.roughness = 0.05; m.metalness = 0.1; m.envMapIntensity = 1.6; m.opacity = Math.max(m.opacity, 0.45);
          m.color.multiplyScalar(0.7);
        } else if (cat && CATS[cat]) {
          // lawn/terrain colours averaged from aerial-draped materials come out grey: give them a lawn tone
          if (cat === 'grass') { const hsl = {}; m.color.getHSL(hsl); if (hsl.s < 0.18 || hsl.l > 0.45) m.color.setHSL(0.21, 0.32, Math.min(0.32, Math.max(0.2, hsl.l * 0.6))); }
          texturize(m, cat);
        }
      }
    });
    register(root);
    addLamps(root);
    shadowDirty = true;
  }
  function reset() { items = []; lampPoints = []; glow.geometry.deleteAttribute('position'); shadowDirty = true; }
  return {
    applyQuality, update, render, renderPlain, decorate, setPaint, setSun, resize, reset, sun,
    invalidateShadows() { shadowDirty = true; },
    get quality() { return qName; }, get scale() { return applied; }, get night() { return night; },
  };
}

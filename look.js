// Look and performance layer for the campus viewer: sky + image-based light, sun shadows,
// AgX tone mapping, fog, ambient occlusion, world-space CC0 textures per material category,
// painted lot markings, and screen-size culling (cheap LOD) with a quality toggle.
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
  bark: { file: 'bark', size: 1.0, k: 0.8 },
};
const ROUGH = { asphalt: 0.92, concrete: 0.85, brick: 0.88, plaster: 0.9, rooftile: 0.75, pavers: 0.85, grass: 1, mulch: 1, gravel: 0.95, stone: 0.7, metal: 0.45, wood: 0.8, bark: 0.95 };
// relief strength from each texture's displacement (alpha channel); fades out by 80 m
const BUMP = { asphalt: 0.35, concrete: 0.3, brick: 1.4, plaster: 0.12, rooftile: 1.5, pavers: 1.1, grass: 0.8, mulch: 1.2, gravel: 1.1, stone: 0.5, metal: 0.1, wood: 0.5, bark: 2 };
// image-based (sky) reflection: rough ground and masonry reflect little of it
const ENV = { asphalt: 0.22, concrete: 0.28, pavers: 0.28, grass: 0.3, mulch: 0.25, gravel: 0.25, stone: 0.4, plaster: 0.45, brick: 0.4, rooftile: 0.5, metal: 1, wood: 0.45, bark: 0.3 };
// slight colour warmth per category, applied after texturing (sky-lit shade otherwise reads blue)
const WARM = { asphalt: [1.1, 1.0, 0.84], concrete: [1.05, 1.0, 0.92], pavers: [1.04, 1.0, 0.94] };

// fix-ups for materials the export categorised by name only
export function fixCat(name, cat) {
  if (cat === 'glass' && /lawn|grass|turf/i.test(name)) return 'grass';
  if (cat === 'asphalt' && /slot_/i.test(name)) return /brick/i.test(name) ? 'brick' : '';
  if (cat) return cat;
  if (/^Bark_/i.test(name)) return 'bark';
  if (/barrel_tile|tile_course|Eave_tile/i.test(name)) return 'rooftile';
  if (/soffit|fascia/i.test(name)) return 'plaster';
  if (/BD_osm_light|BD_fill_massing/i.test(name)) return 'concrete';
  return '';
}

export const QUALITY = {
  low: { pixelRatio: 1, shadows: 0, ao: false, cull: 0.02, tex: true, macro: false },
  medium: { pixelRatio: 1, shadows: 2048, ao: false, cull: 0.008, tex: true, macro: true },
  high: { pixelRatio: 2, shadows: 4096, ao: true, cull: 0.003, tex: true, macro: true },
};

export function createLook(renderer, scene, camera) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.8;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // --- sky and sun (afternoon, from the south-west) ---
  const sky = new Sky(); sky.scale.setScalar(18000); sky.material.fog = false;
  const u = sky.material.uniforms;
  u.turbidity.value = 3.2; u.rayleigh.value = 1.1; u.mieCoefficient.value = 0.004; u.mieDirectionalG.value = 0.82;
  const sunDir = new THREE.Vector3().setFromSphericalCoords(1, THREE.MathUtils.degToRad(90 - 38), THREE.MathUtils.degToRad(215));
  u.sunPosition.value.copy(sunDir);
  scene.add(sky);
  const HORIZON = new THREE.Color('#c6d4e1');
  scene.fog = new THREE.FogExp2(HORIZON, 0.00016);
  scene.background = HORIZON;

  // image-based light from the same sky (gives glass and metal something to reflect)
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene(); const envSky = new Sky(); envSky.scale.setScalar(1000);
  Object.assign(envSky.material.uniforms, THREE.UniformsUtils.clone(u)); envSky.material.uniforms.sunPosition.value.copy(sunDir);
  envScene.add(envSky);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(900, 32).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: '#5d6247' }));
  ground.position.y = -5; envScene.add(ground);
  scene.environment = pmrem.fromScene(envScene, 0.02).texture;
  scene.environmentIntensity = 0.3;

  const hemi = new THREE.HemisphereLight('#e2e7ee', '#4f4a3a', 0.2); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff0dc', 2.7);
  sun.shadow.bias = -0.0002; sun.shadow.normalBias = 0.04;
  scene.add(sun, sun.target);

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
    m.envMapIntensity = ENV[cat] ?? 0.5;
    const isAsphalt = cat === 'asphalt';
    const warm = WARM[cat];
    m.onBeforeCompile = sh => {
      sh.uniforms.tpMap = { value: texFor(cat) };
      sh.uniforms.tpScale = { value: 1 / def.size };
      sh.uniforms.tpK = { value: def.k };
      sh.uniforms.tpMacro = macroUniform;
      sh.uniforms.tpBump = { value: BUMP[cat] ?? 1 };
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
          uniform sampler2D tpMap; uniform float tpScale; uniform float tpK; uniform float tpMacro; uniform float tpBump;
          float tpH = 0.5;
          ${isAsphalt ? 'uniform sampler2D pMap[4]; uniform vec4 pBox[4]; uniform int pN;' : ''}
          vec4 tpSample(vec3 p, vec3 w) {
            return texture2D(tpMap, p.zy) * w.x + texture2D(tpMap, p.xz) * w.y + texture2D(tpMap, p.xy) * w.z;
          }`)
        .replace('#include <map_fragment>', `#include <map_fragment>
          {
            vec3 w = pow(abs(normalize(vTpNrm)), vec3(4.0)); w /= (w.x + w.y + w.z);
            vec4 t4 = tpSample(vTpPos * tpScale, w);
            tpH = t4.a;
            vec3 t = t4.rgb;
            if (tpMacro > 0.5) t = mix(t, tpSample(vTpPos * tpScale * 0.13 + 0.37, w).rgb, 0.35);
            t *= 2.7; // textures are normalised to a mid-grey mean (sRGB 160 ~ linear 0.37)
            diffuseColor.rgb *= mix(vec3(1.0), t, tpK);
            ${warm ? `{ float l = dot(diffuseColor.rgb, vec3(0.2126, 0.7152, 0.0722)); diffuseColor.rgb = mix(diffuseColor.rgb, vec3(l), 0.55) * vec3(${warm.map(x => x.toFixed(3)).join(',')}); }` : ''}
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
          }`)
        .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
          roughnessFactor = clamp(roughnessFactor * (0.9 + 0.25 * (1.0 - tpH)), 0.04, 1.0);`)
        .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
          {
            float fade = clamp(1.0 - length(vViewPosition) / 80.0, 0.0, 1.0);
            vec2 dH = vec2(dFdx(tpH), dFdy(tpH)) * tpBump * fade;
            vec3 sx = dFdx(-vViewPosition), sy = dFdy(-vViewPosition);
            vec3 r1 = cross(sy, normal), r2 = cross(normal, sx);
            float det = dot(sx, r1);
            vec3 g = sign(det) * (dH.x * r1 + dH.y * r2);
            normal = normalize(abs(det) * normal - g);
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
      if (bs.radius > 400) o.castShadow = false; // far-field ground: receives only
    });
  }
  let cullK = QUALITY.medium.cull, lastCull = 0;
  function cull(force) {
    const now = performance.now(); if (!force && now - lastCull < 200) return; lastCull = now;
    const p = camera.position;
    for (const it of items) {
      const d = Math.max(1, p.distanceTo(it.c) - it.r);
      it.o.visible = it.r > d * cullK;
    }
  }

  let q = QUALITY.medium, qName = 'medium';
  function applyQuality(name) {
    qName = name; q = QUALITY[name];
    renderer.setPixelRatio(Math.min(devicePixelRatio, q.pixelRatio));
    renderer.shadowMap.enabled = q.shadows > 0; sun.castShadow = q.shadows > 0;
    if (q.shadows) { sun.shadow.mapSize.set(q.shadows, q.shadows); sun.shadow.map?.dispose(); sun.shadow.map = null; }
    cullK = q.cull; macroUniform.value = q.macro ? 1 : 0;
    if (q.ao && !composer) buildComposer();
    scene.traverse(o => { if (o.material) for (const m of [].concat(o.material)) m.needsUpdate = true; });
    resize(); cull(true);
  }
  function resize() {
    const w = innerWidth, h = innerHeight;
    if (composer) { composer.setPixelRatio(renderer.getPixelRatio()); composer.setSize(w, h); }
  }

  const focus = new THREE.Vector3();
  function update(target) {
    // shadow box follows what you look at; sized to the view distance, snapped to texels
    focus.copy(target ?? camera.position);
    const dist = camera.position.distanceTo(focus);
    const half = THREE.MathUtils.clamp(dist * 0.9, 45, 700);
    const sc = sun.shadow.camera;
    if (sc.right !== half) { sc.left = -half; sc.right = half; sc.top = half; sc.bottom = -half; sc.near = 10; sc.far = 4000; sc.updateProjectionMatrix(); }
    const texel = (2 * half) / (q.shadows || 2048);
    focus.x = Math.round(focus.x / texel) * texel; focus.z = Math.round(focus.z / texel) * texel;
    sun.target.position.copy(focus); sun.position.copy(focus).addScaledVector(sunDir, 1500);
    sky.position.copy(camera.position);
    cull(false);
  }
  function render() {
    if (q.ao && composer) composer.render(); else renderer.render(scene, camera);
  }
  function decorate(root) {
    root.traverse(o => {
      if (!o.isMesh) return;
      for (const m of [].concat(o.material)) {
        if (!m) continue;
        const cat = fixCat(m.name || '', m.userData?.cat || '');
        if (cat !== 'glass' && cat !== (m.userData?.cat || '')) m.userData.glass = false;
        if ((m.userData?.glass || cat === 'glass') && !m.userData.glassDone) {
          m.userData.glassDone = true; // shared materials: tint once
          if (/lamp|globe|frost|opal|led/i.test(m.name)) { m.roughness = 0.4; m.envMapIntensity = 0.6; continue; }
          // windows: dark, smooth and partly metallic so they mirror the sky and trees like real glazing
          m.roughness = 0.03; m.metalness = 0.55; m.envMapIntensity = 1.5; m.opacity = Math.max(m.opacity, 0.82);
          m.color.lerp(new THREE.Color('#22303a'), 0.75);
        } else if (cat && CATS[cat]) {
          // lawn/terrain colours averaged from aerial-draped materials come out grey: give them a lawn tone
          if (cat === 'grass') { const hsl = {}; m.color.getHSL(hsl); if (hsl.s < 0.18 || hsl.l > 0.45) m.color.setHSL(0.21, 0.32, Math.min(0.32, Math.max(0.2, hsl.l * 0.6))); }
          texturize(m, cat);
        }
      }
    });
    register(root);
  }
  function reset() { items = []; }
  return { applyQuality, update, render, decorate, setPaint, resize, reset, sun, get quality() { return qName; } };
}

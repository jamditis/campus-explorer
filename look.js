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
import { fixTone, finishMetal } from './viewer/tone.js';
import { fixCat, isSeeThroughSolid } from './viewer/cat.js';
export { fixTone, fixCat };

// metres per texture repeat, and how strongly the texture modulates the model's own colour
const CATS = {
  asphalt: { file: 'asphalt', size: 3.5, k: 0.8 },
  concrete: { file: 'concrete', size: 2.5, k: 0.7 },
  brick: { file: 'brick', size: 2.2, k: 0.9 },
  plaster: { file: 'plaster', size: 3, k: 0.6 },
  rooftile: { file: 'rooftile', size: 2, k: 0.9 },
  pavers: { file: 'pavers', size: 2, k: 0.85 },
  grass: { file: 'grass', size: 2.4, k: 0.9 },
  turf: { file: 'grass', size: 1.4, k: 0.45 }, // artificial turf: finer and more even than lawn, and it carries painted lines
  mulch: { file: 'mulch', size: 1.6, k: 0.9 },
  gravel: { file: 'gravel', size: 1.5, k: 0.8 },
  stone: { file: 'stone', size: 1.8, k: 0.6 },
  metal: { file: 'metal', size: 1, k: 0.35 },
  wood: { file: 'wood', size: 1.2, k: 0.7 },
  bark: { file: 'bark', size: 1.0, k: 0.8 },
};
const ROUGH = { asphalt: 0.92, concrete: 0.85, brick: 0.88, plaster: 0.9, rooftile: 0.75, pavers: 0.85, grass: 1, turf: 0.9, mulch: 1, gravel: 0.95, stone: 0.7, metal: 0.45, wood: 0.8, bark: 0.95 };
// relief strength from each texture's displacement (alpha channel); fades out by 80 m
const BUMP = { asphalt: 0.35, concrete: 0.3, brick: 1.4, plaster: 0.12, rooftile: 1.5, pavers: 1.1, grass: 0.8, turf: 0.4, mulch: 1.2, gravel: 1.1, stone: 0.5, metal: 0.1, wood: 0.5, bark: 2 };
// image-based (sky) reflection: rough ground and masonry reflect little of it
const ENV = { asphalt: 0.22, concrete: 0.28, pavers: 0.28, grass: 0.3, turf: 0.3, mulch: 0.25, gravel: 0.25, stone: 0.4, plaster: 0.45, brick: 0.4, rooftile: 0.5, metal: 1, wood: 0.45, bark: 0.3 };
// tangent-space normal maps (ambientCG NormalGL, CC0) for these categories, applied triplanar; strength
const NRM = { asphalt: 0.8, concrete: 0.7, brick: 1, plaster: 0.6, rooftile: 1, pavers: 1, grass: 0.8, turf: 0.4, mulch: 1, gravel: 1, wood: 0.7, bark: 1.2 };
// slight colour warmth per category, applied after texturing (sky-lit shade otherwise reads blue)
// [r, g, b, desaturation]; plaster keeps its own colour (cream and white stucco) and only loses the sky-blue cast
const WARM = { asphalt: [1.04, 1.0, 0.92, 0.55], concrete: [1.05, 1.0, 0.92, 0.55], pavers: [1.04, 1.0, 0.94, 0.55], plaster: [1.05, 1.0, 0.92, 0] };

export const QUALITY = {
  low: { pixelRatio: 1, shadows: 0, ao: false, cull: 0.02, tex: true, macro: false },
  medium: { pixelRatio: 1.5, shadows: 2048, ao: false, cull: 0.008, tex: true, macro: true },
  high: { pixelRatio: 2, shadows: 4096, ao: true, cull: 0.003, tex: true, macro: true },
};
const COARSE = matchMedia('(pointer: coarse)').matches;
const MIN_SCALE = 0.5; // lowest resolution scale the governor may use while the view moves
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const FILLER = /^(WS62_crown_|MID_street_trunk|Icosphere\.?001$)/; // far-field filler; glTF names drop the dot
const CROWN = new THREE.MeshStandardMaterial({ color: '#6b6a3c', roughness: .95 });

/** `onChange` is called when something drawn changed without the camera moving (a texture arrived). */
export function createLook(renderer, scene, camera, onChange = () => {}) {
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
  // aerial perspective: about 15% haze at 1.5 km and 25% at 2 km on a clear afternoon (was ~6% and 10%)
  scene.fog = new THREE.FogExp2(HORIZON, 0.00027);
  scene.background = HORIZON;

  // image-based light from the same sky (gives glass and metal something to reflect)
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene(); const envSky = new Sky(); envSky.scale.setScalar(1000);
  Object.assign(envSky.material.uniforms, THREE.UniformsUtils.clone(u));
  envScene.add(envSky);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(900, 32).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: '#6b6456' }));
  // bounce from the ground: lawn, asphalt and stucco average out to a warm grey, not olive (olive plus blue sky
  // left every shaded wall cyan)
  ground.position.y = -5; envScene.add(ground);
  let envTarget = null; const envDir = new THREE.Vector3();
  function bakeEnvironment() {
    envSky.material.uniforms.sunPosition.value.copy(sunDir);
    const next = pmrem.fromScene(envScene, 0.02);
    scene.environment = next.texture; envTarget?.dispose(); envTarget = next; envDir.copy(sunDir);
  }
  // the sky light is a saturated cyan; with it at 0.3 shaded white stucco read teal (rgb ~102,112,117 on screen).
  // Less of it and a neutral hemisphere fill keep shade cool but closer to grey
  scene.environmentIntensity = 0.22;

  const SKY_DAY = new THREE.Color('#e9e9e7'), SKY_NIGHT = new THREE.Color('#33415f');
  const SOIL_DAY = new THREE.Color('#4f4a3a'), SOIL_NIGHT = new THREE.Color('#12151c');
  const SUN_HIGH = new THREE.Color('#fff0dc'), SUN_LOW = new THREE.Color('#ff9a4d');
  const hemi = new THREE.HemisphereLight(SKY_DAY, SOIL_DAY, 0.3); scene.add(hemi);
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
    hemi.intensity = 0.3 + 0.4 * (1 - day);
    HORIZON.copy(NIGHT_FOG).lerp(DAY_FOG, day).lerp(DUSK_FOG, low * day * 0.6);
    scene.fog.color.copy(HORIZON); // FogExp2 keeps its own copy of the colour
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
  const lamps = new Map(); // tile root -> [x, y, z, ...]
  function showLamps() {
    const all = [].concat(...lamps.values());
    if (all.length) glow.geometry.setAttribute('position', new THREE.Float32BufferAttribute(all, 3)); else glow.geometry.deleteAttribute('position');
  }
  function addLamps(root) {
    const m = new THREE.Matrix4(), p = new THREE.Vector3(), lampPoints = []; let n = 0;
    root.traverse(o => {
      if (!o.isInstancedMesh || !/^Lamp_/i.test(o.name)) return;
      const bb = o.geometry.boundingBox ?? (o.geometry.computeBoundingBox(), o.geometry.boundingBox);
      for (let i = 0; i < o.count; i++) {
        o.getMatrixAt(i, m); m.premultiply(o.matrixWorld);
        p.set((bb.min.x + bb.max.x) / 2, bb.max.y - (bb.max.y - bb.min.y) * 0.08, (bb.min.z + bb.max.z) / 2).applyMatrix4(m);
        lampPoints.push(p.x, p.y, p.z); n++;
      }
    });
    if (n) { lamps.set(root, lampPoints); showLamps(); }
  }

  // --- flat far ground for the lite profile, which leaves out the 4 km terrain skirt ---
  const farGround = new THREE.Mesh(new THREE.CircleGeometry(9000, 48).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: '#8b9070', roughness: 1 }));
  farGround.name = 'ground_far'; farGround.receiveShadow = true; farGround.visible = false; scene.add(farGround);
  /** Show a flat ground disc at height `y` under (x, z), or hide it with `on` false. */
  function setFarGround(on, x = 0, y = 0, z = 0) { farGround.visible = on; farGround.position.set(x, y, z); }


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
    onChange(); // the view may be still when the texture arrives
  });
  const nrmFor = c => texCache[c + '_n'] ??= loader.load(`./textures/${CATS[c].file}_n.webp`, t => {
    t.colorSpace = THREE.NoColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.needsUpdate = true;
    onChange();
  });
  let paint = []; // [{tex, x0,x1,z0,z1}]
  // paint layers (one webp mask per modelling session that painted markings); every layer is a sampler on
  // asphalt materials, and WebGL2 guarantees 16 per shader, so 8 leaves room for the textures and shadows
  const PAINT_MAX = 8;
  const paintUniforms = { pMap: { value: [] }, pBox: { value: [] }, pN: { value: 0 } };
  const EMPTY = new THREE.DataTexture(new Uint8Array(4), 1, 1); EMPTY.needsUpdate = true;
  const paintTex = url => { const t = loader.load(url, onChange); t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  function setPaint(list, base) {
    if (list.length > PAINT_MAX) console.warn('paint layers beyond', PAINT_MAX, 'ignored:', list.slice(PAINT_MAX).map(p => p.file));
    paint = list.slice(0, PAINT_MAX).map(p => ({ ...p, tex: paintTex(base + p.file) }));
    const maps = [], boxes = [];
    for (let i = 0; i < PAINT_MAX; i++) {
      const p = paint[i];
      maps.push(p ? p.tex : EMPTY);
      // Blender (x, y) -> three (x, -z)
      boxes.push(p ? new THREE.Vector4(p.x0, -p.y1, p.x1 - p.x0, p.y1 - p.y0) : new THREE.Vector4(0, 0, 1, 1));
    }
    paintUniforms.pMap.value = maps; paintUniforms.pBox.value = boxes; paintUniforms.pN.value = paint.length;
  }
  const macroUniform = { value: 1 };

  function texturize(m, cat) {
    const def = CATS[cat]; if (!def || m.userData.tp) return;
    m.userData.tp = cat;
    if (ROUGH[cat] !== undefined && !m.roughnessMap) m.roughness = ROUGH[cat];
    if (cat !== 'metal') m.metalness = 0;
    m.envMapIntensity = ENV[cat] ?? 0.5;
    const isAsphalt = cat === 'asphalt';
    if (isAsphalt && !m.map) {
      // asphalt colours sampled from the ortho come out far too pale (up to linear 0.58, like fresh concrete);
      // real pavement reflects about 0.05 (new) to 0.2 (old, grey). Keep each surface's relative tone, in that range.
      const l = m.color.r * 0.2126 + m.color.g * 0.7152 + m.color.b * 0.0722;
      if (l > 0) m.color.multiplyScalar(THREE.MathUtils.clamp(l * 0.42, 0.06, 0.19) / l);
    }
    const warm = WARM[cat];
    const hasN = NRM[cat] !== undefined;
    const painted = /_painted_/.test(m.name); // a paint sheet of the southwest build (blender/southwest/paint.py)
    m.onBeforeCompile = sh => {
      sh.uniforms.tpMap = { value: texFor(cat) };
      sh.uniforms.tpScale = { value: 1 / def.size };
      sh.uniforms.tpK = { value: def.k };
      sh.uniforms.tpMacro = macroUniform;
      sh.uniforms.tpBump = { value: BUMP[cat] ?? 1 };
      if (hasN) { sh.uniforms.tpNMap = { value: nrmFor(cat) }; sh.uniforms.tpNStr = { value: NRM[cat] }; }
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
          ${hasN ? 'uniform sampler2D tpNMap; uniform float tpNStr;' : ''}
          float tpH = 0.5;
          ${isAsphalt ? `uniform sampler2D pMap[${PAINT_MAX}]; uniform vec4 pBox[${PAINT_MAX}]; uniform int pN;` : ''}
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
            ${warm ? `{
              float l = dot(diffuseColor.rgb, vec3(0.2126, 0.7152, 0.0722)), desat = ${warm[3].toFixed(2)};
              ${painted ? `
                // a surface with its own paint sheet: coloured paint (yellow lines, red letters) keeps its colour
                float chroma = max(diffuseColor.r, max(diffuseColor.g, diffuseColor.b)) - min(diffuseColor.r, min(diffuseColor.g, diffuseColor.b));
                desat *= 1.0 - smoothstep(0.15, 0.45, chroma / max(l, 0.001));` : ''}
              diffuseColor.rgb = mix(diffuseColor.rgb, vec3(l), desat) * vec3(${warm.slice(0, 3).map(x => x.toFixed(3)).join(',')});
            }` : ''}
            ${isAsphalt ? `
            for (int i = 0; i < ${PAINT_MAX}; i++) {
              if (i >= pN) break;
              vec2 uv = (vTpPos.xz - pBox[i].xy) / pBox[i].zw;
              if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) continue;
              vec4 pc;
              // sampler arrays need constant indices in GLSL
              ${Array.from({ length: PAINT_MAX }, (_, k) => `${k ? 'else ' : ''}if (i == ${k}) pc = texture2D(pMap[${k}], uv);`).join(' ')}
              diffuseColor.rgb = mix(diffuseColor.rgb, pc.rgb * mix(1.0, t.r, 0.25), pc.a);
            }` : ''}
          }`)
        .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
          roughnessFactor = clamp(roughnessFactor * (0.9 + 0.25 * (1.0 - tpH)), 0.04, 1.0);`)
        .replace('#include <normal_fragment_maps>', hasN ? `#include <normal_fragment_maps>
          {
            // triplanar normal map, whiteout blend (world space), added to the view-space normal
            float fade = clamp(1.0 - length(vViewPosition) / 120.0, 0.0, 1.0);
            vec3 Nw = normalize(vTpNrm);
            vec3 w = pow(abs(Nw), vec3(4.0)); w /= (w.x + w.y + w.z);
            vec3 p = vTpPos * tpScale;
            vec3 tx = texture2D(tpNMap, p.zy).xyz * 2.0 - 1.0;
            vec3 ty = texture2D(tpNMap, p.xz).xyz * 2.0 - 1.0;
            vec3 tz = texture2D(tpNMap, p.xy).xyz * 2.0 - 1.0;
            vec3 nx = vec3(tx.xy + Nw.zy, abs(tx.z) * Nw.x);
            vec3 ny = vec3(ty.xy + Nw.xz, abs(ty.z) * Nw.y);
            vec3 nz = vec3(tz.xy + Nw.xy, abs(tz.z) * Nw.z);
            vec3 Nb = normalize(nx.zyx * w.x + ny.xzy * w.y + nz.xyz * w.z);
            normal = normalize(normal + mat3(viewMatrix) * (Nb - Nw) * tpNStr * fade);
          }` : `#include <normal_fragment_maps>
          {
            float fade = clamp(1.0 - length(vViewPosition) / 80.0, 0.0, 1.0);
            // once a pixel spans a texel or more (grazing angles, thin strips such as granite curbs) the height
            // derivative is noise and the bump turns into black and white speckle: fade it out there
            float fp = length(fwidth(vTpPos)) * tpScale;
            fade *= clamp(1.0 - (fp - 0.0008) / 0.0012, 0.0, 1.0); // gone by ~1 texel per pixel (1/512 of a repeat)
            vec2 dH = vec2(dFdx(tpH), dFdy(tpH)) * tpBump * fade;
            vec3 sx = dFdx(-vViewPosition), sy = dFdy(-vViewPosition);
            vec3 r1 = cross(sy, normal), r2 = cross(normal, sx);
            float det = dot(sx, r1);
            vec3 g = sign(det) * (dH.x * r1 + dH.y * r2);
            normal = normalize(abs(det) * normal - g);
          }`);
    };
    m.customProgramCacheKey = () => 'tp_' + cat + (painted ? '_painted' : '');
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
      if (o.userData.treeLod) return; // trees.js culls these per instance
      if (bs.radius < 120) items.push({ o, c: bs.center, r: bs.radius, root });
      else o.visible = true;
      if (bs.radius > 400) o.castShadow = false; // far-field ground: receives only
    });
  }
  let cullK = QUALITY.medium.cull, lastCull = 0;
  function cull(force) {
    const now = performance.now(); if (!force && now - lastCull < 200) return; lastCull = now;
    const p = camera.position;
    for (const it of items) {
      if (it.o.userData.treeLod) continue; // trees.js culls these per instance
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
      if (!on) { sun.shadow.map?.dispose(); sun.shadow.map = null; } // up to 4096² of GPU memory
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
    else if (!q.ao && composer) { gtao.dispose?.(); composer.dispose?.(); composer = gtao = null; }
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
    // phone screens are dense: one device pixel per CSS pixel looks soft, so Low still gets 1.5 there
    const cap = COARSE && qName === 'low' ? 1.5 : q.pixelRatio;
    renderer.setPixelRatio(Math.min(devicePixelRatio, cap) * s);
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
    const far = farGround.visible;
    scene.fog = null; sky.visible = false; glow.visible = false; farGround.visible = false;
    // screen-size culling was decided for the main camera: show everything for this one, then cull again
    for (const it of items) if (!it.o.userData.treeLod) it.o.visible = true;
    renderer.setRenderTarget(target); renderer.render(scene, cam); renderer.setRenderTarget(null);
    scene.fog = fog; sky.visible = true; glow.visible = night > 0.02; farGround.visible = far; sun.shadow.needsUpdate = auto;
    cull(true);
  }
  function fixMaterials(root) {
    root.traverse(o => {
      if (!o.isMesh) return;
      if (root.name === 'context' && FILLER.test(o.name)) { o.visible = false; o.userData.filler = o.userData.hidden = true; return; } // float above the exported skirt
      if (/^Icosphere/.test(o.name)) { o.material = CROWN; return; }
      for (const m of [].concat(o.material)) {
        if (!m) continue;
        if (m.map) m.map.anisotropy = /_painted_/.test(m.name) ? 16 : 4; // paint sheets lie flat and are seen at grazing angles
        // leaf cards exported without an opacity map would show their white texture background: draw them as solid foliage
        if (/^Leaf_|needle/i.test(m.name) && !(m.alphaTest > 0) && !m.transparent) { m.map = null; m.color.set('#4f5a33'); m.side = THREE.DoubleSide; m.needsUpdate = true; continue; }
        if (m.alphaTest > 0 || (m.transparent && m.map)) { m.alphaTest = 0.45; m.transparent = false; m.side = THREE.DoubleSide; m.userData.leaf = true; }
        // see-through and not glazing (fence fabric, netting) keeps its category and stays see-through
        else if (m.transparent) { m.depthWrite = false; m.userData.glass = !isSeeThroughSolid(m.name || '', m.userData.cat || ''); }
      }
    });
  }
  // Interior mapping: fake rooms behind vertical window glass. World-space cells (3.6 m bays,
  // 3.4 m storeys, 5 m deep) aligned to each facade; per-room tint and lights from a hash of the cell.
  function glassInterior(m) {
    m.onBeforeCompile = sh => {
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vGiPos; varying vec3 vGiNrm;')
        .replace('#include <begin_vertex>', `#include <begin_vertex>
          vGiPos = (modelMatrix * vec4(transformed, 1.0)).xyz; vGiNrm = normalize(mat3(modelMatrix) * objectNormal);`);
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
          varying vec3 vGiPos; varying vec3 vGiNrm;
          float giHash(vec3 c) { return fract(sin(dot(c, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }`)
        .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
          {
            vec3 Nw = normalize(vGiNrm);
            if (!gl_FrontFacing) Nw = -Nw;
            vec3 V = normalize(vGiPos - cameraPosition);
            if (abs(Nw.y) < 0.5 && dot(V, Nw) < 0.0) {
              vec3 N = normalize(vec3(Nw.x, 0.0, Nw.z)), T = vec3(-N.z, 0.0, N.x);
              const vec3 CELL = vec3(3.6, 3.4, 5.0);
              vec3 p = vec3(dot(vGiPos, T), vGiPos.y, 0.0) / CELL;
              vec3 d = vec3(dot(V, T), V.y, -dot(V, N)) / CELL;
              vec3 cell = floor(p); vec3 f = vec3(fract(p.xy), 0.0);
              float tx = ((d.x > 0.0 ? 1.0 : 0.0) - f.x) / d.x;
              float ty = ((d.y > 0.0 ? 1.0 : 0.0) - f.y) / d.y;
              float tz = 1.0 / max(d.z, 1e-4);
              float t = min(min(tx, ty), tz);
              vec3 h = f + d * t;
              float rnd = giHash(cell + floor(dot(vGiPos, N) * 0.2));
              vec3 wall = mix(vec3(0.62, 0.6, 0.56), vec3(0.55, 0.58, 0.62), rnd);
              vec3 col;
              if (t == tz) col = wall * (0.75 + 0.25 * h.y);                    // back wall
              else if (t == tx) col = wall * (0.55 + 0.35 * (1.0 - h.z));       // side walls, darker deeper in
              else col = d.y > 0.0 ? vec3(0.8, 0.8, 0.78) * (0.6 + 0.4 * h.z)   // ceiling
                                   : vec3(0.32, 0.26, 0.2) * (0.6 + 0.4 * (1.0 - h.z)); // floor
              float lit = step(0.45, fract(rnd * 7.13));                        // some rooms have lights on
              col *= mix(0.16, 0.42, lit) * (1.0 - 0.5 * h.z);
              float fres = 0.04 + 0.96 * pow(1.0 - clamp(dot(-V, Nw), 0.0, 1.0), 5.0);
              totalEmissiveRadiance += col * (1.0 - fres);
            }
          }`);
    };
    m.customProgramCacheKey = () => 'glass_interior';
    m.needsUpdate = true;
  }
  // lamp heads often reuse a building's clear window glass, which the window treatment turns near-black:
  // give lamp meshes their own frosted (opal) globe with a faint warm glow instead
  const LAMP_RE = /lamp|acorn|lantern|bollard_light|light_pole|streetlight/i;
  const opals = new Map();
  function opalFor(m) {
    if (!opals.has(m)) {
      const g = new THREE.MeshStandardMaterial({ name: m.name + '_opal', color: '#f1ece2', roughness: 0.45, metalness: 0, emissive: '#ffd9a0', emissiveIntensity: 0.18 });
      g.userData = { cat: 'glass', glass: true, glassDone: true }; opals.set(m, g);
    }
    return opals.get(m);
  }
  function swapMat(o, m, g) { o.material = Array.isArray(o.material) ? o.material.map(x => (x === m ? g : x)) : g; }
  // Sports surfaces (turf, courts) are modelled at the same level as the terrain under them, which z-fights
  // into a blotchy half-field from a distance. Pull them (and their line markings) forward in depth.
  const SPORT_RE = /turf|court|track_surface|pitch_surface/i, LINES_RE = /lines|markings/i;
  function liftSportSurfaces(root) {
    const surf = [], lines = [];
    root.traverse(o => { if (!o.isMesh) return; if (SPORT_RE.test(o.name)) surf.push(o); else if (LINES_RE.test(o.name)) lines.push(o); });
    if (!surf.length) return;
    const lift = (o, k) => {
      const mats = [].concat(o.material).map(m => { const c = m.clone(); c.polygonOffset = true; c.polygonOffsetFactor = -k; c.polygonOffsetUnits = -k; return c; });
      o.material = mats.length === 1 ? mats[0] : mats;
    };
    for (const o of surf) lift(o, 1);
    for (const o of lines) lift(o, 2);
  }
  /** Prepare one loaded tile (or its far version): material fixes, textures, culling registration, lamps. */
  function decorate(root) {
    fixMaterials(root);
    liftSportSurfaces(root); // before texturing: a cloned material does not keep its shader hook
    root.traverse(o => {
      if (!o.isMesh) return;
      const lamp = LAMP_RE.test(o.name) || LAMP_RE.test(o.parent?.name || '');
      for (const m of [].concat(o.material)) {
        if (!m) continue;
        if (lamp && (m.userData?.glass || m.userData?.cat === 'glass')) { swapMat(o, m, opalFor(m)); continue; }
        // Aerial-draped terrain can come out as asphalt (its image names mention roads); it is plain ground.
        // The exporter does not know this yet, so the viewer corrects it by material name.
        const raw = /(ground|skirt)_ortho/i.test(m.name) ? 'grass' : m.userData?.cat || '';
        const cat = fixCat(m.name || '', raw);
        fixTone(m.name || '', m.color, !!m.map);
        if (cat !== 'glass' && cat !== (m.userData?.cat || '')) m.userData.glass = false;
        if ((m.userData?.glass || cat === 'glass') && !m.userData.glassDone) {
          m.userData.glassDone = true; // shared materials: tint once
          if (/lamp|globe|frost|opal|led/i.test(m.name)) { m.roughness = 0.4; m.envMapIntensity = 0.6; continue; }
          // windows: dark, smooth glazing that mirrors the sky at grazing angles, with rooms behind it
          m.roughness = 0.03; m.metalness = 0.15; m.envMapIntensity = 1.4;
          m.color.lerp(new THREE.Color('#1c262e'), 0.8);
          if (o.isInstancedMesh || m.side === THREE.BackSide) { m.opacity = Math.max(m.opacity, 0.82); continue; }
          m.transparent = false; m.opacity = 1; m.depthWrite = true; glassInterior(m);
        } else if (cat && CATS[cat]) {
          // lawn/terrain colours averaged from aerial-draped materials come out grey: give them a lawn tone
          if (cat === 'grass') { const hsl = {}; m.color.getHSL(hsl); if (hsl.s < 0.18 || hsl.l > 0.45) m.color.setHSL(0.21, 0.32, Math.min(0.32, Math.max(0.2, hsl.l * 0.6))); }
          texturize(m, cat);
          finishMetal(m.name || '', m);
        }
      }
    });
    register(root);
    addLamps(root);
    shadowDirty = true;
  }
  /** Forget a tile that was dropped from memory. */
  function forget(root) { items = items.filter(it => it.root !== root); if (lamps.delete(root)) showLamps(); shadowDirty = true; }
  function reset() { items = []; lamps.clear(); showLamps(); farGround.visible = false; shadowDirty = true; }
  return {
    applyQuality, update, render, renderPlain, decorate, forget, setFarGround, setPaint, setSun, resize, reset, sun,
    invalidateShadows() { shadowDirty = true; },
    get quality() { return qName; }, get scale() { return applied; }, get night() { return night; },
  };
}

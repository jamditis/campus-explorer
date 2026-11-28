// The night sky over the campus: the bright stars where they really are for the instant shown, and
// the moon at its real position and phase. One draw call each, nothing per frame but following the
// camera. The star list (viewer/stars.json, 24 kB) loads the first time the sun is low enough for
// stars to show, so a daytime visit never fetches it.
import * as THREE from 'three';
import { CAMPUS, convergenceDeg } from './geo.js';
import { equatorialToHorizon, moonPosition, starBrightness, starColor, starsShown } from './sky-math.js';

const R = 31000;          // sphere the stars and moon are drawn on; inside the camera's far plane (app.js)
const MOON_DEG = 0.52;    // the moon's angular diameter, drawn at its real size
const HALO = 6;           // the moon's quad is this many times the disc, for the glow round it
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

/**
 * @param app the shared app object (see docs/VIEWER.md)
 * @returns {{ readonly stars: number, readonly moon: object|null }}
 */
export function createSky(app) {
  const { scene, camera } = app;
  const group = new THREE.Group(); group.name = 'night_sky'; scene.add(group);
  // equatorial frame -> viewer frame (x east, y up, -z grid north); grid north is a fraction of a degree east of true north
  const turn = new THREE.Matrix4(), toViewer = new THREE.Matrix4();
  const conv = THREE.MathUtils.degToRad(convergenceDeg(CAMPUS.lat, CAMPUS.lon));
  // [east, north, up] -> [x, y, z]: x = east, y = up, z = -north; then turn about y by the grid convergence
  toViewer.set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1).premultiply(new THREE.Matrix4().makeRotationY(conv));

  // ---- stars ----
  const starMat = new THREE.ShaderMaterial({
    uniforms: { shown: { value: 0 }, pxScale: { value: 1 } },
    vertexShader: /* glsl */`
      attribute vec3 tint; attribute float bright;
      uniform float shown; uniform float pxScale;
      varying vec3 vTint;
      void main() {
        vec4 w = modelMatrix * vec4(position, 1.0);
        vec3 dir = normalize(w.xyz - cameraPosition);
        // haze and the glow of the region's lights swallow stars low in the sky
        float clear = smoothstep(0.03, 0.3, dir.y);
        vTint = tint * min(1.2, 0.12 + 2.2 * bright) * shown * clear;
        gl_PointSize = (1.6 + 2.8 * bright) * pxScale;
        gl_Position = projectionMatrix * viewMatrix * w;
      }`,
    fragmentShader: /* glsl */`
      varying vec3 vTint;
      void main() {
        vec2 c = gl_PointCoord - 0.5;
        float a = smoothstep(0.5, 0.1, length(c));
        gl_FragColor = vec4(vTint * a, 1.0);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, toneMapped: false,
  });
  const stars = new THREE.Points(new THREE.BufferGeometry(), starMat);
  stars.name = 'stars'; stars.frustumCulled = false; stars.visible = false; stars.renderOrder = -1; stars.matrixAutoUpdate = false;
  group.add(stars);
  let starCount = 0, starsWanted = false, starsLoading = false;
  async function loadStars() {
    try {
      const doc = await (await fetch('./viewer/stars.json')).json();
      const n = doc.stars.length, pos = new Float32Array(n * 3), tint = new Float32Array(n * 3), bright = new Float32Array(n);
      doc.stars.forEach(([ra, dec, vmag, bv], i) => {
        const a = THREE.MathUtils.degToRad(ra), d = THREE.MathUtils.degToRad(dec);
        pos.set([Math.cos(d) * Math.cos(a) * R, Math.cos(d) * Math.sin(a) * R, Math.sin(d) * R], i * 3);
        tint.set(starColor(bv), i * 3);
        bright[i] = starBrightness(vmag);
      });
      const g = stars.geometry;
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      g.setAttribute('tint', new THREE.BufferAttribute(tint, 3));
      g.setAttribute('bright', new THREE.BufferAttribute(bright, 1));
      starCount = n; place(); app.invalidate();
    } catch (e) { console.warn('stars did not load', e); } finally { starsLoading = false; } // a later time change tries again
  }

  // ---- moon: a camera-facing disc lit from the sun's direction, so its phase and the side it is lit from are right ----
  const moonMat = new THREE.ShaderMaterial({
    uniforms: { sunDir: { value: new THREE.Vector3(0, 1, 0) }, shown: { value: 0 }, day: { value: 0 } },
    vertexShader: /* glsl */`
      varying vec2 vUv; varying vec3 vRight; varying vec3 vUp; varying vec3 vToward;
      void main() {
        vUv = uv * 2.0 - 1.0;
        // a quad that faces the camera, with its own axes in world space for the lighting
        vec3 centre = (modelMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
        vToward = normalize(cameraPosition - centre);
        vRight = normalize(cross(vec3(0.0, 1.0, 0.0), vToward)); vUp = cross(vToward, vRight);
        float s = length(modelMatrix[0].xyz);
        vec3 w = centre + (vRight * position.x + vUp * position.y) * s;
        gl_Position = projectionMatrix * viewMatrix * vec4(w, 1.0);
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 sunDir; uniform float shown; uniform float day;
      varying vec2 vUv; varying vec3 vRight; varying vec3 vUp; varying vec3 vToward;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453); }
      void main() {
        vec2 p = vUv * ${HALO.toFixed(1)}; // in disc radii
        float r2 = dot(p, p);
        // output is premultiplied (blendSrc One): the glow adds, the disc covers the sky
        if (r2 > 1.0) {
          // a soft glow round the disc (moonlight scattered in the haze), stronger the fuller the moon
          float full = 0.5 + 0.5 * dot(vToward, sunDir);
          float g = exp(-(sqrt(r2) - 1.0) * 1.1) * 0.45 * full * shown * (1.0 - day);
          gl_FragColor = vec4(vec3(0.85, 0.87, 0.9) * g, 0.0);
          return;
        }
        vec3 n = vRight * p.x + vUp * p.y + vToward * sqrt(1.0 - r2);
        float lit = smoothstep(-0.04, 0.08, dot(n, sunDir));
        // maria: a few dark patches, fixed to the disc (the moon keeps one face to the Earth)
        float m = 0.0;
        m += smoothstep(0.32, 0.0, length(p - vec2(-0.25, 0.3)));
        m += smoothstep(0.26, 0.0, length(p - vec2(0.15, 0.25)));
        m += smoothstep(0.3, 0.0, length(p - vec2(0.05, -0.15)));
        m += smoothstep(0.22, 0.0, length(p - vec2(-0.4, -0.05)));
        float albedo = 1.0 - 0.28 * clamp(m, 0.0, 1.0) - 0.05 * hash(floor(p * 9.0));
        vec3 c = vec3(0.98, 0.96, 0.9) * albedo * (lit + 0.025); // + earthshine on the dark side
        float edge = smoothstep(1.0, 0.92, r2);
        // by day the moon is a pale disc against the blue, only its lit part shows
        float a = edge * shown * mix(1.0, lit * 0.55, day);
        gl_FragColor = vec4(c * mix(1.0, 1.25, day) * a, a);
      }`,
    transparent: true, depthWrite: false, fog: false, toneMapped: false,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
  });
  const moon = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), moonMat);
  moon.name = 'moon'; moon.frustumCulled = false; moon.visible = false; moon.renderOrder = -1;
  moon.scale.setScalar(2 * HALO * R * Math.tan(THREE.MathUtils.degToRad(MOON_DEG / 2)));
  group.add(moon);
  let moonNow = null;

  function place() {
    const date = app.time?.date; if (!date) return;
    const el = app.sun?.elevation ?? 90;
    // stars
    const k = starsShown(el);
    starsWanted ||= k > 0;
    if (starsWanted && !starCount && !starsLoading) { starsLoading = true; loadStars(); }
    const m = equatorialToHorizon(date, CAMPUS.lat, CAMPUS.lon);
    turn.set(m[0], m[1], m[2], 0, m[3], m[4], m[5], 0, m[6], m[7], m[8], 0, 0, 0, 0, 1).premultiply(toViewer);
    stars.matrix.copy(turn); stars.matrixWorldNeedsUpdate = true;
    starMat.uniforms.shown.value = k; stars.visible = k > 0 && starCount > 0;
    // moon
    moonNow = moonPosition(date, CAMPUS.lat, CAMPUS.lon);
    const b = THREE.MathUtils.degToRad(moonNow.azimuth) - conv, e = THREE.MathUtils.degToRad(moonNow.elevation);
    moon.position.set(Math.sin(b) * Math.cos(e), Math.sin(e), -Math.cos(b) * Math.cos(e)).multiplyScalar(R);
    const sb = THREE.MathUtils.degToRad(app.sun.azimuth) - conv, se = THREE.MathUtils.degToRad(el);
    moonMat.uniforms.sunDir.value.set(Math.sin(sb) * Math.cos(se), Math.sin(se), -Math.cos(sb) * Math.cos(se));
    // the moon dims into the haze near the horizon; it is hidden below it
    const up = smooth(-0.5, 4, moonNow.elevation);
    moonMat.uniforms.day.value = smooth(-6, 4, el);
    moonMat.uniforms.shown.value = up;
    moon.visible = up > 0;
    app.look.setMoon(moonNow.fraction * up);
  }
  const follow = () => { group.position.copy(camera.position); };
  const onResize = () => { starMat.uniforms.pxScale.value = Math.min(2, app.renderer.getPixelRatio()); };
  app.on('sun', place);
  app.on('camera', follow);
  app.on('quality', onResize); app.on('resize', onResize);
  // renderPlain (the minimap) draws without the sky
  return {
    get stars() { return starCount; },
    get moon() { return moonNow; },
    setVisible(on) { group.visible = on; },
  };
}

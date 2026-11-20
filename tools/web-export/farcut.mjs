// Very distant buildings (the New York and Jersey City skyline, American Dream, 11 to 30 km east of the campus)
// as one light silhouette instead of their 3D meshes. Past FAR_M (10 km) the viewer's fog (look.js, FogExp2
// 0.00027) leaves under 0.1 % of a surface's own colour and a 30 m wide building is under 3 pixels wide at
// the walk view's 68 degree field of view on a 1080 px screen: all that shows is the outline against the sky.
// The stand-in keeps that outline as seen from the campus centre (skyline.mjs): a curtain through the tops of
// the source triangles, at their true bearings, distances and heights.
//   node farcut.mjs FILE.glb [FILE.glb ...]
// Rewrites a file in place only when it holds such meshes; a later export brings them back and this step,
// run again by build_web.sh after the context tile is optimized, replaces them again. Ground (terrain, the
// far-field 3DEP surface) is never cut. Env: FAR_M (10000), STEP (bin, degrees, 0.1: 1.2 to 1.6 px), TOL (degrees, 0.05: under a pixel),
// EYE_Z (eye height at the campus centre, NAVD88 m, 138: LiDAR ground 136.7 plus eye height), REACH (0).
// The viewer's far plane (app.js, 20 km) cuts off every part of the 3D skyline past 20 km from the camera,
// most of Manhattan seen from the campus: REACH=17000 keeps the whole outline inside it from anywhere in the
// flight box (2 km round the centre), at the same bearings and elevation angles from the campus centre.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { prune } from '@gltf-transform/functions';
import { statSync, writeFileSync } from 'node:fs';
import { profile, simplify, curtain, beyond } from './skyline.mjs';
import { keepShared, sharedRefs } from './tex.mjs';

const FAR_M = +(process.env.FAR_M || 10000), STEP = +(process.env.STEP || 0.1), TOL = +(process.env.TOL || 0.05);
const EYE = [0, 0, +(process.env.EYE_Z || 138)];
// REACH (m, 0: none): bring stand-in points past it nearer along their sight line (skyline.mjs curtain)
const REACH = +(process.env.REACH || 0);
const NAME = 'BD_skyline_silhouette_STANDIN';
const GROUND = /terrain|DTM|ground|farfield|3DEP|skirt|apron|ortho|road|street/i;

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });

/** World-space triangles of a node's mesh in the model frame (viewer y up, z south -> z up, y north). */
function triangles(node) {
  const W = node.getWorldMatrix(), out = [];
  const tf = p => [W[0] * p[0] + W[4] * p[1] + W[8] * p[2] + W[12], W[1] * p[0] + W[5] * p[1] + W[9] * p[2] + W[13], W[2] * p[0] + W[6] * p[1] + W[10] * p[2] + W[14]];
  for (const prim of node.getMesh().listPrimitives()) {
    const pos = prim.getAttribute('POSITION'), idx = prim.getIndices(); if (!pos || prim.getMode() !== 4) continue;
    const v = [], el = [];
    for (let i = 0; i < pos.getCount(); i++) { const w = tf(pos.getElement(i, el)); v.push([w[0], -w[2], w[1]]); }
    const n = idx ? idx.getCount() : pos.getCount();
    for (let i = 0; i < n; i++) out.push(...v[idx ? idx.getScalar(i) : i]);
  }
  return out;
}

for (const f of process.argv.slice(2)) {
  const doc = await io.read(f), root = doc.getRoot(), before = statSync(f).size, { json } = await io.readAsJSON(f);
  const uris = root.listTextures().map(t => t.getURI());
  const far = [], tris = [], old = []; // old: a stand-in an earlier run left
  for (const node of root.listNodes()) {
    const mesh = node.getMesh();
    if (!mesh || node.getExtension('EXT_mesh_gpu_instancing') || GROUND.test(node.getName()) || GROUND.test(mesh.getName())) continue;
    if (node.getName() === NAME) { old.push(node); continue; }
    const t = triangles(node);
    if (!beyond(t, FAR_M)) continue;
    far.push(node); for (const v of t) tris.push(v);
  }
  if (!far.length) { console.log(`farcut ${f.split('/').pop()}: nothing past ${FAR_M} m`); continue; }
  const prof = profile(Float64Array.from(tris), EYE, STEP), runs = simplify(prof, TOL), c = curtain(runs, prof, EYE, REACH);
  // to the viewer frame (x east, y up, z south)
  const P = new Float32Array(c.position.length), N = new Float32Array(c.normal.length);
  for (let i = 0; i < P.length; i += 3) {
    P[i] = c.position[i]; P[i + 1] = c.position[i + 2]; P[i + 2] = -c.position[i + 1];
    N[i] = c.normal[i]; N[i + 1] = c.normal[i + 2]; N[i + 2] = -c.normal[i + 1];
  }
  const buf = root.listBuffers()[0] ?? doc.createBuffer();
  const mat = doc.createMaterial(`${NAME}_haze`).setBaseColorFactor([0.42, 0.47, 0.53, 1]).setRoughnessFactor(1).setMetallicFactor(0).setDoubleSided(true);
  const prim = doc.createPrimitive().setMaterial(mat)
    .setAttribute('POSITION', doc.createAccessor().setType('VEC3').setArray(P).setBuffer(buf))
    .setAttribute('NORMAL', doc.createAccessor().setType('VEC3').setArray(N).setBuffer(buf))
    .setIndices(doc.createAccessor().setType('SCALAR').setArray(c.index).setBuffer(buf));
  const node = doc.createNode(NAME).setMesh(doc.createMesh(NAME).addPrimitive(prim));
  const scene = root.getDefaultScene() ?? root.listScenes()[0];
  let gone = 0;
  for (const n of [...far, ...old]) { gone += far.includes(n); n.dispose(); }
  scene.addChild(node);
  // only what the removed meshes leave unused: nodes the viewer reads by name stay
  await doc.transform(prune({ keepLeaves: true, keepAttributes: true, keepExtras: true, keepSolidTextures: true }));
  // write with the method the file has: filtered (optimize) or plain quantized (lod.mjs), so nothing loses precision
  const filtered = (json.bufferViews ?? []).some(v => (v.extensions?.EXT_meshopt_compression?.filter ?? 'NONE') !== 'NONE');
  const { FILTER, QUANTIZE } = EXTMeshoptCompression.EncoderMethod;
  root.listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: filtered ? FILTER : QUANTIZE });
  writeFileSync(f, keepShared(await io.writeBinary(doc), sharedRefs(uris, f, f)));
  const after = statSync(f).size;
  console.log(`farcut ${f.split('/').pop()}: ${gone} meshes past ${FAR_M} m (${tris.length / 9} triangles) -> ${NAME} `
    + `(${c.index.length / 3} triangles, ${runs.length} runs), ${(before / 1e6).toFixed(2)} -> ${(after / 1e6).toFixed(2)} MB`);
}

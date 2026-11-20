// Trees used 2 to 4 times in a tile as GPU instances (EXT_mesh_gpu_instancing), before `optimize`.
//   node tree_instance.mjs RAW.glb [RAW.glb ...]   (rewrites each file in place; TREE_MIN=2 by default)
// `optimize --instance` instances a mesh only when 5 or more nodes use it, and `--join` then merges
// the copies of a tree used 2 to 4 times into one plain mesh holding every copy's vertices (29 MB of
// the scripted tiles when this was written). Here every `Tree_*` mesh used by TREE_MIN or more nodes
// becomes one batch, as gltf-transform's instance() builds it; optimize skips nodes that are
// instances already. Only trees (pack.mjs treeBatches): benches, lamps and other fixtures in small
// groups stay joined, because the viewer collides with joined meshes and not with instances.
import { NodeIO, MathUtils } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshGPUInstancing } from '@gltf-transform/extensions';
import { dedup } from '@gltf-transform/functions';
import { treeBatches } from './pack.mjs';

const MIN = +(process.env.TREE_MIN || 2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const IDENTITY = { TRANSLATION: [0, 0, 0], ROTATION: [0, 0, 0, 1], SCALE: [1, 1, 1] };

// One batch for `nodes` (all using `mesh`) at the scene root, with each node's world TRS as an
// instance, as instance() writes it. False when every copy sits at the origin unturned.
function makeBatch(doc, ext, scene, mesh, nodes) {
  const buffer = mesh.listPrimitives()[0].getAttribute('POSITION').getBuffer();
  const values = {
    TRANSLATION: nodes.map(n => n.getWorldTranslation()),
    ROTATION: nodes.map(n => n.getWorldRotation()),
    SCALE: nodes.map(n => n.getWorldScale()),
  };
  const batch = ext.createInstancedMesh();
  let any = false;
  for (const [key, list] of Object.entries(values)) {
    if (list.every(v => MathUtils.eq(v, IDENTITY[key]))) continue;
    const a = doc.createAccessor().setType(key === 'ROTATION' ? 'VEC4' : 'VEC3')
      .setArray(new Float32Array(list.flat())).setBuffer(buffer);
    batch.setAttribute(key, a);
    any = true;
  }
  if (!any) { batch.dispose(); return false; }
  scene.addChild(doc.createNode().setMesh(mesh).setExtension('EXT_mesh_gpu_instancing', batch));
  return true;
}

// Drop nodes left with nothing (no mesh, children or extensions), then their emptied parents,
// as instance() does.
function pruneEmpty(nodes) {
  let n;
  while ((n = nodes.pop())) {
    if (n.listChildren().length || n.getCamera() || n.getMesh() || n.getSkin()) continue;
    if (n.listExtensions().length) continue;
    const p = n.getParentNode(); if (p) nodes.push(p);
    n.dispose();
  }
}

for (const f of process.argv.slice(2)) {
  const doc = await io.read(f), root = doc.getRoot(), tile = f.split('/').pop();
  if (root.listAnimations().length) { console.log(`trees ${tile}: animated, left as it is`); continue; }
  // link identical meshes first (optimize starts with the same dedup), so copies that Blender wrote
  // out as separate meshes are counted together
  await doc.transform(dedup());
  const ext = doc.createExtension(EXTMeshGPUInstancing);
  let batches = 0, instances = 0;
  for (const scene of root.listScenes()) {
    const list = [];
    scene.traverse(n => list.push(n));
    const entries = list.map(n => ({
      mesh: n.getMesh(), name: n.getMesh()?.getName(), skin: !!n.getSkin(),
      instanced: !!n.getExtension('EXT_mesh_gpu_instancing'),
    }));
    const emptied = [];
    for (const ix of treeBatches(entries, MIN)) {
      const nodes = ix.map(i => list[i]);
      if (!makeBatch(doc, ext, scene, nodes[0].getMesh(), nodes)) continue;
      for (const n of nodes) { n.setMesh(null); emptied.push(n); }
      batches++; instances += nodes.length;
    }
    pruneEmpty(emptied);
  }
  if (!ext.listProperties().length) ext.dispose();
  await io.write(f, doc);
  console.log(`trees ${tile}: ${batches} batches, ${instances} instances`);
}

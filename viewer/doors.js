// Entrance doors that open in walk mode (#119). The build marks each moving leaf: a node named DOOR_<building>_
// <entrance>_<leaf> with extras `door` (viewer/doors-math.js). This module finds those leaves in every tile that
// loads, opens a door when the walker comes near and faces it, and closes it after they leave. The leaf moves by
// its world matrix (doors-math leafMove); a door open past DOOR_PASS stops colliding (world.js skips meshes with
// userData.doorOpen), so the walker can go through. Nothing runs outside walk mode, where every door is shut.
import * as THREE from 'three';
import { doorFrom, wantsOpen, stepOpen, leafMove, DOOR_PASS } from './doors-math.js';

/** @param app the shared app object (docs/VIEWER.md) */
export function createDoors(app) {
  const doors = new Map(); // id -> { leaves: [{ o, door (its own hinge or travel), root, base (world), parentInv }], at, s }
  const _m = new THREE.Matrix4(), _box = new THREE.Box3(), _look = new THREE.Vector3();

  function add(root) {
    root.updateMatrixWorld(true);
    root.traverse(o => {
      if (!o.name.startsWith('DOOR_')) return;
      const door = doorFrom(o.userData.door); if (!door) return;
      let d = doors.get(door.id);
      if (!d) doors.set(door.id, d = { leaves: [], at: new THREE.Vector3(), s: 0 });
      o.matrixAutoUpdate = false;
      d.leaves.push({ o, door, root, base: o.matrixWorld.clone(), parentInv: o.parent ? o.parent.matrixWorld.clone().invert() : new THREE.Matrix4() });
      _box.makeEmpty(); for (const l of d.leaves) _box.expandByObject(l.o); _box.getCenter(d.at);
      if (d.s > 0) pose(d); // a leaf that streams in while its door is open takes the door's pose and collision
    });
  }
  function remove(root) {
    for (const [id, d] of doors) {
      const n = d.leaves.length; d.leaves = d.leaves.filter(l => l.root !== root);
      if (!d.leaves.length) doors.delete(id);
      else if (d.leaves.length !== n) { _box.makeEmpty(); for (const l of d.leaves) _box.expandByObject(l.o); _box.getCenter(d.at); }
    }
  }
  function pose(d) {
    const open = d.s >= DOOR_PASS;
    for (const l of d.leaves) { // the leaves of a door open together, each about its own hinge or along its own travel
      _m.fromArray(leafMove(l.door, d.s));
      l.o.matrix.copy(l.parentInv).multiply(_m).multiply(l.base); // local = parent⁻¹ · move · shut world
      l.o.traverse(m => { if (m.isMesh) m.userData.doorOpen = open; });
      app.world.refit(l.o); // collision boxes follow the leaf (it updates the leaf's world matrices)
    }
  }
  function step(dt) {
    if (!doors.size) return;
    const walking = app.state.mode === 'walk' && app.player.placed;
    if (walking) app.camera.getWorldDirection(_look);
    let moved = false;
    for (const d of doors.values()) {
      const want = walking && wantsOpen(d.at, app.player.position, { x: _look.x, z: _look.z }, d.s > 0);
      const s = walking ? stepOpen(d.s, want, dt) : 0; // outside walk mode every door is shut at once
      if (s === d.s) continue;
      d.s = s; pose(d); moved = true;
    }
    if (moved) { app.look.invalidateShadows(); app.invalidate(); }
  }
  app.on('tile', ({ tile }) => add(tile.root));
  app.on('scene:start', () => doors.clear());
  app.on('frame', ({ dt }) => step(dt));
  return {
    /** How far open (0 to 1) the door `id` is, or null when no loaded tile has it. */
    open: id => doors.get(id)?.s ?? null,
    get count() { return doors.size; },
    /** Forget the leaves of a tile that was dropped from memory (world.js release, with the root itself). */
    forget: remove,
  };
}

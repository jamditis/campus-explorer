# ws259 runbook (Nov 27, 2026, 2:35 → ~3:10 AM ET) — UNIFY #2 applied, UNIFY #6 walk joints, low-memory subset crop

Main before: ws257d (sha 79938a4c…). Backup montclair_state_pre_20261127ws259.blend = ws257d. Chain via `run259.sh` (= ws257/run257.sh, grep tags added; ws208/merge208.py CHAIN, base meshes, ~1.8 GB):
ws257d + `../ws258/f258a.py` → ws259a (Footpaths_OSM 15,869 → 15,802 faces, 67/67 matched); ws259a + `f259b.py` → ws259b = MAIN.

1. `f259b.py` (UNIFY #6): WS259_UNIFY6_CollegeAve_S_W_walk_sawcut_1p524m_UNVERIFIED on WS103 — centreline from 0.5 m y-bins of the walk's top-face verts,
   transverse cuts every 1.524 m (56 runs, 2.76–3.54 m long), same strip build/material as ws257 f257a. Object names must stay ≤ 63 chars
   (a 64-char first name was silently truncated by Blender, so EXTRAJ could not find it).
2. `crop259.py` (render-only subset CHAIN): crop257 applied to every `bpy.data` world-space mesh > CROPV (20k) verts, including drape/target
   objects that GN Object Info pulls into the depsgraph but that are not linked to the scene. Subset render peak 7.8 GB → 2.65 GB VmHWM.
3. Renders: `jobwip259.sh` (subrend234, terrain GN on, CROPM 40, EXTRAJ extra259.json for the new strips). batch1 = BEFORE (main ws257d) close-up + ws259a views.
4. Probes: `probe259c/d/f.py` (subset CHAINs, exit before render) and `probe259e.py` (merge208 CHAIN, no save): ground beside the WS103 walk → new UNIFY W64
   (no ground object W of the walk's S half except the skirt, pushed under by its GN; UNVERIFIED whether the full scene shows a hole).
5. W64 follow-up: `probe259g.py` (FULL main, all modifiers, VmHWM 7.6 GB): only the skirt (117.4–118.2) W of the walk's S half, 2.2–2.4 m below its edge, so it is a real hole.
   `las259.py` / `las259b.py` (geo venv /workspace/opt/geo/bin/python3; J5D6 for x ≥ −268, J5D5 W of it) → prep/ws259_w64/dtm259.npy (box only): verge level
   with the walk, then a bank to ~118.7 m. `probe259h.py` (1 m full-scene mask via scene.ray_cast) was too slow (killed at 10 min). Next: build the BVH from evaluated meshes.

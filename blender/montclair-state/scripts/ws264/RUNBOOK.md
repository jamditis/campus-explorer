# ws264 runbook (Fri Nov 27, 2026, 12:29 → ~1:15 PM ET) — M5 pre-release cleanup (no visible model change)

Main before: ws263g (sha 247d25a8…). Backup montclair_state_pre_20261127ws264.blend = ws263g. Chain via `run264.sh`
(= ws263/run263.sh with F264/P264/C264 tags; ws208/merge208.py, base meshes, peak ~1.9 GB): ws263g + `f264c.py` → ws264c = MAIN.

1. `probe264a.py` (open main, no save): who references WS113_paving_tops_proxy and the 113 empty mesh stubs; list the
   12 absolute paths. Proxy: 82,716 v, 188 NaN, 74 faces touch them; hidden; only user = node group WS113_paving_edge_grade.
   Empty stubs: 110 with no modifiers / children / references; 3 carry GN modifiers (they generate their geometry).
   Absolute paths: 2 local images (data/ts/naip_far, naip_skirt_4k), 6 library paths (assets/*.blend), 4 images that live
   inside assets/campus_assets.blend (SweetgumStar_*, TulipPoplar_*).
2. `f264a.py` (REJECTED, staging deleted): relativise + delete the NaN verts + remove the 110 stubs. `m5check264.py EVAL=1`
   (evaluates only the WS113_paving_edge_grade users, everything else's modifiers off) vs ws263g: 37 ground verts moved,
   up to 0.48 m lower at the Chapin W plaza edge (−216, −202) and S of Chapin → the NaN faces' finite corners were feeding
   the grade.
3. `f264b.py` (REJECTED, staging deleted): same but repair NaN verts by neighbour mean (88 in all-NaN islands deleted) →
   51 verts moved by up to 1.1 m. Worse.
4. `f264c.py` = MAIN: relativise 8 main-owned paths (2 images + 6 libraries), remove the 110 unreferenced empty stubs (names in
   f264c_removed_stubs.txt), LEAVE the NaN proxy as-is. EVAL hashes of all 4 grade users identical to ws263g.
5. Asset stream (assets/.lock): `a264a.py` relativises the 4 leaf-texture paths inside assets/campus_assets.blend
   (//textures/…). Backup assets/campus_assets_pre_ws264.blend.
6. `m5check264.py` on ws264c: 0 absolute paths (main-owned or inside linked libraries), 0 missing files, 0 unresolved
   libraries, 0 paths outside the project or under north/, 1 NaN mesh (the proxy, kept on purpose), 3 empty meshes (GN
   generators), 10,496 objects / 10,174 in scene (was 10,606 / 10,284). Opening the file fresh in background Blender = the open-test.
7. WIPs `jobwip264.sh` (subrend234, terrain GN on, crop259): police overview/eye (EXTRAJ ws262/extra262p.json + KEEPMOD
   grass points), W66 eye and Chapin W plaza edge close-up (EXTRAJ ws263/extra263.json).

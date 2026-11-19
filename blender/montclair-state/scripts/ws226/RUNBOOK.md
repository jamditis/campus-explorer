# ws226 runbook (Nov 19, 2026 ~1:33-~2:20 AM ET): W53 east terrain upper sheet, tree re-seat, W54 apron lawn shoulder, W55 subset-render fix
Main before: ws225a (9990e96e...). Main after: ws226f (promoted ~1:55 AM ET). Each step = `INF=<in> OUTN=<out> CHAIN="ws226/<fix>.py" bash scripts/ws226/run226.sh`
(run226.sh = run225.sh: memory-gated merge208 runner, all modifiers off at load, DNA-poke restore).
- ws226a = ws225a + fix226a: delete 14 base Terrain_LiDAR_DTM_1m faces in the east (centre x>60, >100 m2) that are 100% under the
  QG/QH/QI LiDAR patches (probe226f.json); the biggest is ONE 21,272 m2 interpolated quad centred (163,50) that sat 3-13 m above
  the 1 m DTM (and the USGS 3DEP 10 m DEM, data/skirt_dem_10m.npy). Its re-seat of 30 trees used the lowest vertex (wrong for PinOak,
  see fix226b).
- ws226b = ws226a + fix226b: trees re-seated by their trunk-base ring (local z~0): (a) raise-only scene-wide where the terrain agrees
  with dtm_1m within 0.7 m (68 trees), (b) the 30 fix226a trees re-seated both ways (23 moved).
- ws226c = ws226b + fix226c: 19 WQ_south_wood_tree_* woodland trees seated on the corrected NE slope.
- ws226d = ws226c + fix226d: NEW WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED (W54; 18 m2 grass shoulder along the SE/E apron edge).
- ws226e = ws226d + fix226e: delete 142 sliver fan faces (apex (216.4,248.5,122.9)) fully under the LiDAR patches.
- ws226f = ws226e + fix226f: NEW WS226_east_patch_seam_backing_UNVERIFIED (backing skin 8 cm under the terrain at the 58 hole samples
  fix226a uncovered along patch seams; holes226.json from probe226n before/after).
- Probes: probe226a (stack + grid vs DTM), b (QG/QH/QI node trees), c/d (per-modifier heights), e/f (base face sizes/coverage),
  g (grid after fix), h/j (tree trunk vs terrain), i (tree mesh trunk rings), k (apron edge drops), l (fan slivers), m (camera ray),
  n (terrain hole count). runp.sh runs a probe with all modifiers off at load (INF= to pick a file).
- subrend226.py (+ srun226.sh): subrend212 that also appends wanted objects missing from main from LIBS (default
  north/sprague_cafe_src.blend), because main LINKS the 649 Sprague/Cafe Diem objects and libraries.load(main) lists only local ones (W55).
- jobdiag226.sh / jobtest226.sh: before/after tests; jobwip226.sh: the four WIPs.

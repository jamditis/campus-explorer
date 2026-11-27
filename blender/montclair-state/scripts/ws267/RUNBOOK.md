# ws267 runbook (Fri Nov 27, 2026, 6:31 → ~7:40 PM ET) — police S terrace-bed lawn, pale deck-base strip, pre-release check

Main before: ws266b (sha 0ec04cbc…). Backup montclair_state_pre_20261127ws267.blend = ws266b. Chain via `run267.sh`
(= ws266/run266.sh with F267/P267/C267 tags; ws208/merge208.py, base meshes; CHAIN paths are relative to scripts/):
ws266b + `f267a.py` → ws267a; + `f267b.py` → ws267b; + `f267c.py` → ws267c = MAIN.

0. Pre-release check. `m5run267.sh` (plain `blender -b main --python ws264/m5check264.py`, gate 7 GB) was watchdog-killed at
   1.39 GB 23 s after starting with 7.3 GB available: opening main without merge208 evaluates the full scene. `m5wrap267.py`
   runs the same check inside merge208's loader (modifiers off at load_post, nothing evaluated, no save): peak 1.3 GB, 5 s.
   Result on ws266b and on ws267c: 0 paths outside montclair-state/ or assets/, 0 absolute, 0 missing, 0 unresolved libs;
   known 1 NaN helper (WS113_paving_tops_proxy, kept since ws264), 3 empty GN carriers, 5 UH-named cameras/points (no geometry).
1. `probe267a.py` (no save): box x −358…−320, y −24…−5 S of the W263 box. The evaluated version (modifiers on) and even
   `evaluated_depsgraph_get()` with modifiers off were watchdog-killed at ~3.2 GB available, and so was reading the ortho
   with `image.pixels[:]` (Python float list of a 2023×4096 image). Working version: base meshes (`o.data`), one BVHTree per
   mesh, 0.35 m jittered samples → eval267a.json; ortho colour sampled outside Blender from the UV (linear UV fit, residual
   < 1e-4, ortho_uv_fit.json). Finding: S of the box the "bare strip" is the sunken bed inside the white terrace walls
   (ge_police_terrace_bed, x −353…−339, y −18…−11, z 121.6–122.9) with material ge_bed_soil and no blades; the 2020 ortho shows it
   uniform mown green. Other ground S of the box is pale = paving/road in the ortho (not lawn).
2. `f267a.py`: 5,563 points precomputed outside Blender (bed267a_points.json: 64 pts/m², 0.15 m off the terrace walls with the
   ws266 trimmed-edge easing, z = IDW of 4 bed samples − 1 cm; the bed has no modifiers so base z = rendered z) appended to
   gd_grass_police_lawn_points (53,383 → 58,946).
3. `f267b.py` (f266a pattern, eval265a evaluated-ground samples): pale deck-base strip — ground samples with ortho luminance
   ≥ 0.85 at x > −337 (436 samples, a band x −335…−324 along the deck W face where the ortho shows the deck's own white roof
   edge through building lean). Deficit fill to core density (66/m²), 0.3 m off the deck / deck-base strip / walks with a 0.3 m
   fade, 3 m fade at the N/S box edges only. 2,814 points (58,946 → 61,760). W263 soil mask rebuilt from the points inside the
   box only (the bed points are S of it) as //data/ws267/police_grass_density267b.png.
4. `f267c.py`: ge_bed_soil (1 user, the bed) base colour mixed 0.8 toward the W263 olive, roughness 1, specular 0.1, so the
   soil between blades reads as thatch, not pale bald patches (close-up before/after: wip 1847 ws267b vs 1849 ws267c).
5. WIPs `jobwip267.sh` (subrend234, terrain GN on, crop259, EXTRAJ ws262/extra262p.json + KEEPMOD grass points).

# ws254 runbook (Nov 26, 2026, 4:30 → ~5:2x PM ET) — UNIFY W63e: Feliciano E recess stairs to the wall + entrance doors, flight A grass dip, walk N end joined

Main before: ws253g (sha 0408fe49…). Backup montclair_state_pre_20261126ws254.blend = ws253g. MAIN = ws254d (saved 4:50:51 PM ET, promoted 4:51:39 PM ET, sha d4cd58a9…; sha254d.txt). Chain: ws253g + `f254a.py` → ws254a, + `f254b.py` → b, + `f254c.py` → c (first promote 4:47:46 PM ET), + `f254d.py` → d. Staging a/b/c deleted; copy montclair_state_ws254d.blend (= main) kept.

1. `probe254.py` / `probe254b.py` (read-only, library load): evaluated ground grid x −199…−186, y 160…186 (recess x −197.6…−195.2 at 135.7–136.7 m over y 168.5–172, i.e. 0.3–0.6 m above the landing/flight B treads); Feliciano E wall by horizontal rays: x −197.56 (y 166.5) → −197.26 (y 171.5), −194.69 from y 172; nothing south of y 166.3 (building corner); base-course band PI on the recess wall; OSM footpath starts at y ≈ 190.8 (x −191…−190.4, 138.81 m).
2. `crop254.py` (ortho crop, box only, kept off the repo): the light N–S strip x −192…−189.5 runs north into the building's shadow; no other walk visible → straight extension (UNVERIFIED in the shadow).
3. `f254a.py` (CHAIN via ws208/merge208.py, `run254.sh`):
   - apron WS253_W63d_Feliciano_E_recess_apron_raise_only_UNVERIFIED removed;
   - Terrain_LiDAR_DTM_1m base mesh bisected along x −197.6 / −195.0, y 163.8 / 172.0 and the 11 faces inside deleted (W63b method); q254: 0 uncovered holes;
   - W cheek of ws253 (x −195.2…−194.95) deleted; new WS254_W63e_recess_stairs_landing_to_wall_UNVERIFIED: flight A / landing / flight B / walk strip widened west to x −197.62 (W end tucked into the wall), same treads and heights as ws253, abutting its boxes (no coplanar overlap);
   - WS254_W63e_flightA_W_cheek_UNVERIFIED x −197.87…−197.62, y 163.8…166.6 (flight A's west end is exposed south of the building corner), straight cap = nosing + 0.15;
   - WS254_W63e_Feliciano_E_entrance_doors_UNVERIFIED on the recessed wall at the landing (y 166.7…168.5, 135.30 m): aluminium/white frame, two glazed leaves with meeting stiles, bottom rails, transom (2.75 m), pulls; materials North_Feliciano_glass_dark / North_Feliciano_stucco_white;
   - grass dip beside flight A's E cheek: 5 WS251 patch verts in the x −189 column raised back toward the original ground (min(orig, cheek cap − 0.08));
   - WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED x −191.98…−189.5, y 183.5…191.0, draped on max(base, W63 patch) + 6 cm, continuous with the ws253 walk end.
4. `f254b.py`: PI base-course faces on the recessed wall (x < −196.9, y 166…172.2; 12 of 88) deleted (the stepped band followed the old hump and crossed the new doors; test renders/test/20261126-1637/1639_*_ws254a_*).
5. `f254c.py`: the extension's last two rows lowered (top 138.84 at y 190.5, 138.78 at y 191.0) so it dives under the OSM walk start (6 cm lip in test …-1642_*_ws254b_*).
6. `f254d.py` (`lamp254.py` check): Lamp_acorn_031 +0.38 m (was 0.36 m into the ws250 lawn), Lamp_acorn_030 +0.07 m, WS252 plaza lamp +0.03 m → bases 2 cm under the walk/ground surface.
7. Checks `q254.py` (evaluated terrain with GN joins): treads/landing over the deleted terrain (363 covered samples), 0 uncovered holes in x −199…−194, y 162…174; cheek 0.37 m+; extension 1 sample −3 mm at its W edge where it meets the OSM walk; ws253 slabs unchanged (≤ 1.2 cm at 2 edge samples).
8. M2c review (`rev254.py`, read-only): North_NEWalkCurveS_gk → drop (77 % of samples under main ground, 70 % on an existing main walk), North_NEPlaza_gi → deferred (floats up to 1.8 m), ge_police_south_walk → still review (inconclusive) → `m2c_next254.json`.
9. PLAN M4 (`m4probe254.py`, `m4cafe254.py`, read-only): 433 NORTH_MERGE objects vs main: 0 duplicate pairs (IoU > 0.5 + shared material + dims within 20 %). Sprague L0 east strip does not hide Café Diem (it stands above café geometry only over Sprague's own wing x ≤ −54, plus 2 samples at the café's NE corner y ≈ 69.5) → no trim.
10. WIPs `jobwip254.sh` (subrend234, terrain GN on, EXTRAJ extra254.json).

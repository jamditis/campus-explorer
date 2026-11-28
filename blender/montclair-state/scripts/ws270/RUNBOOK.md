# ws270 runbook (Sat Nov 28, 2026, 12:35 → ~1:45 AM ET) — W72c College Ave / Lot 33 paving lift + edge shoulder

Main before: ws269c (sha 669f3abc…). Backup montclair_state_pre_20261128ws270.blend = ws269c.

1. `probe270a.py` (= the f268c ground/fit/lift code, no save; run270.sh, merge208 CHAIN) dumps the 1 m grid (ground Z, quadratic fit F,
   old lift L, old surface S, paving ray z) to probe270a.npz (not in the repo). The paving still equals S (max diff 1.1 cm).
   Findings: the N-edge ridge (lift 0.6–0.75 m at x −365…−359, y −21) comes from ground samples OUTSIDE the polygon (f268c sampled
   edist < 2.5 m and max-filtered 2 m), i.e. the police-lawn foot (+0.5…+1.0 m residual at y −19). The W swells are in-polygon
   mounds (+0.2…+0.5 m) blurred only 1.5 m, so the paving rose in short plateau lumps.
2. `lift270.py` `lift_env`: lift from samples inside the polygon (or < 0.4 m outside) only; 3×3 max, smooth upper envelope
   (20 × L = max(L0, gauss(L, 1.5 m))), 1 m blur, local top-up until no sample is above the surface. Offline on the npz: deficit
   −1 mm, 1 m-Laplacian p95/p99/max 0.034/0.071/0.252 → 0.024/0.048/0.110 m, mean +2.9 cm, range −0.59…+0.15 m.
3. `f270a.py` (run270.sh on ws269c) → ws270a (saved 12:38:54 AM ET, promoted 12:42:58 AM ET): every paving vertex moved by
   S_new − S_old (bilinear), top verts checked against the evaluated WS68 + M3b ground (2 bumped to +3 cm; min 3 cm, p50 17.6 cm);
   dense N-curb check (874 points 0.1–0.6 m inside) min 2.8 cm. ws269 island curb/mulch shifted −1…+8 cm, island tree +3.9 cm.
   No terrain vertices edited (AGENTS.md rule 6: the paving still sits on top of the GN-evaluated terrain everywhere).
   `probe270b.py`: police south walk S edge minus paving 0.5 m S: −0.34…−0.08 m (ws269c) → −0.13…−0.02 m (ws270a).
4. `f270b.py` (on ws270a) → ws270b = MAIN (saved 12:51:44 AM ET, promoted 12:52:40 AM ET): 261 outline skirt verts moved outward
   (2× the drop, 0.25–1.2 m) down to ground − 5 cm where the ground outside is lower (drop p50 0.14 m, max 1.43 m); the 272 shoulder
   faces use the adjacent M3b ground's ortho material (North_ground_ortho2020.001, Object coords, both identity transforms; probe270c).
   A flat lawn material was tried first and read as a bright green band (not kept). 30 skirt verts on inner holes / rising ground
   stay vertical and asphalt.
5. WIPs: `jobwip270.sh` (EXTRA = the ws268 paving + ws269 island objects; terrain GN on via KEEPMOD, crop259). Before views:
   renders/test/…ws269c_before… (cams 3, 4).

# ws271 runbook (Sat Nov 28, 2026, ~2:38 → ~3:20 AM ET) — W72d Lot 33 outline notches + UNIFY #4 grandstand seam

Main before: ws270b (sha f8b019d9…). Backup montclair_state_pre_20261128ws271.blend = ws270b.

1. `probe271a.py` (run271.sh = run270.sh pattern, merge208 CHAIN, no save) dumps the College Ave / Lot 33 paving mesh and the
   evaluated WS68 + M3b ground grid (0.25 m) to probe271a.npz (not in the repo). `loopnotch.py` walks the asphalt top outline:
   one loop, no holes, but reflex notches at the SW corner (11 verts, x −385…−376, y −39…−42, 0.1–0.6 m² each) and at the N edge by
   the police south walk W end (2 verts at (−357/−355, −22)). Each notch vertex is an interior 1 m grid vertex on the outline with a
   0.6 m vertical asphalt skirt under it → the dark sawtooth / notch seen in the ws270 WIPs.
2. `f271a.py` (on ws270b) → ws271a (saved 2:42:39 AM ET, promoted 2:44:42 AM ET): each notch vertex moved onto the straight segment
   between its outline neighbours (z interpolated, ≥ evaluated ground + 3 cm; flip guard scales the move back if a top face would
   flip), its skirt bottom re-interpolated between the neighbours' bottoms (shoulder material where both are shoulders). 12 passes →
   32 moves, 0 notches left in the two windows, 0 downward asphalt faces, 0 top verts below ground + 2.5 cm. No terrain edits.
3. `probe271b.py` / `probe271c.py`: WS86 grandstand GN (core x −249…−234, y −154…−129, 3 m SMOOTHSTEP feather — already smooth).
   `probe271d.py` (first-hit grid with modifiers on for objects in the window, render-hidden helpers excluded; peak 7.6 GB):
   the grandstand lawn is two grounds — WS68_RHD_ground_northDTM W of x −249, Terrain_LiDAR_DTM_1m E — Terrain 0.3–0.7 m higher at
   the seam for y −121…−131.
4. `f271b.py` (on ws271a) → ws271b (saved 2:55:52 AM ET, promoted 2:57:48 AM ET), then after the Codex review → ws271c = MAIN
   (saved 3:06:32 AM ET, promoted 3:08:21 AM ET, sha256 e4364f10…): new GN modifier
   WS271_grandstand_seam_terrain_feather_lower_only on Terrain_LiDAR_DTM_1m right after WS86: delta = min(0, zWS68(−249.5, y) − zTerrain(−248.5, y)),
   offset z by delta × smoothstep(x −249.6 → −243.6) × y-taper (−136…−134 / −121…−119). Seam step after: ≤ 6 cm for y −120…−131.
   Lower only; lawn only (no paving/walks in the band). ws271b had two faults found in review: the new modifier was saved with
   its viewport (Realtime) bit off because merge208 only restores modifiers in _OFF, and its name did not match subrend234's
   terrain regex, so subset renders dropped it. ws271c registers it in _OFF (POKE208 restored 1180) and puts 'terrain' in the
   name; the ws271c grandstand render differs from ws271b only along the seam (x 271–281 px), as expected.
5. Renders: `jobwip271.sh` (Lot 33 cams, terrain GN on via subrend234 + KEEPMOD, crop259) and `gs271.sh` (grandstand cams, GATE 8000,
   peak 6.4 GB). Before/after: renders/test/20261128-0243_…ws270b_before… vs …ws271a… (SW corner close-up);
   renders/test/20261128-0250_…ws271a_sub vs 20261128-0306_…ws271c_sub (grandstand from S, high; the 0256 ws271b render
   did not include the modifier).

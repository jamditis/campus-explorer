# ws266 runbook (Fri Nov 27, 2026, 4:35 → ~5:50 PM ET) — police foundation / outbuilding bare band (ws265 residual)

Main before: ws265b (sha b5e4b852…). Backup montclair_state_pre_20261127ws266.blend = ws265b. Chain via `run266.sh`
(= ws265/run265.sh with F266/P266/C266 tags; ws208/merge208.py, base meshes): ws265b + `f266a.py` → ws266a; + `f266b.py` → ws266b = MAIN.

1. `f266a.py` (no modifier evaluation; reuses ws265/eval265a.json, the 0.35 m ray samples on the evaluated ground): fills the
   grass deficit only within 1.6 m of a non-ground probe top. Building tops (police roof/parapet/windows/foundation/outbuilding/
   roof units) may be approached to 0.15 m with density easing 40% → 100% over 0.6 m (trimmed lawn edge); walks / deck / deck-base
   strip keep 0.3 m clearance with a 0.3 m fade; luminance cut 0.85 (the pale band along the deck face stays bare); 3 m fade at
   the W263 box edge. z = IDW of the 4 nearest ground samples − 2 cm, capped at nearest sample + 5 cm. 2,366 points
   (51,017 → 53,383; list in band266a_points.json, not committed). W263 soil mask rebuilt as //data/ws266/police_grass_density266a.png.
   Peak 1.86 GB.
2. Top-down check renders/test/ws266_police_band_topdown.png (new points hug the police/outbuilding outlines and the deck edge).
3. WIPs `jobwip266.sh` (subrend234, terrain GN on, crop259, EXTRAJ ws262/extra262p.json + KEEPMOD grass points).
   Eye-from-E camera first sat inside the police wall → moved to −333,3,125.1 → −341,−4,124.2.
4. `probe266b.py` (W68 Chapin W stair-landing slit, 5 cm grid on the evaluated scene): first run killed by the watchdog because a
   WIP render was started alongside (my error: only one Blender at a time); second run (farfield/skirt modifiers left off)
   ran > 15 min on scene.ray_cast over the whole depsgraph and was stopped to leave time for the WIPs. Replaced by:
5. `probe266c.py` (no save): BVHTree per evaluated mesh meeting the box (42 objects, 27 trees, no farfield/skirt), 5 cm grid
   x −224…−212, y −208…−196 → eval266c.json (18 s). Finding: the W68 "slit" is an exposed PIT of WS113 terrain fan fill
   x −218.7…−216.9, y −200.35…−201.40 (z 122.61–122.72) between the plaza E-corridor concrete (N, z 122.83–122.90) and the
   S-wing door apron (S, z 122.673): 6 cm below the apron, 15–25 cm below the corridor; seen at grazing angle it reads as a dark slit.
6. `f266b.py` → ws266b: concrete infill (575 pit cells + 82 boundary cells, 601 quads, material Paving_concrete like the apron,
   collection WS117_Chapin_W_main_entrance) whose top is the harmonic (Laplace) interpolation of the surrounding paving tops
   (stair-riser cells take the nearby plaza/apron z), 1-cell overlap under the neighbours at top − 5 mm. Top 122.682–122.884.
   The real joint (ramp vs step) is not visible in the ortho at this scale = UNVERIFIED.
7. W68 WIP: jobwip266.sh ONLY=5 (EXTRAJ extra266.json = extra263 + the new object, because subrend picks objects from the
   precomputed bbox205.json). CULL format is x0,x1,y0,y1. Camera −222.5,−203.5,124.3 → −217.8,−200.9,122.75 (the ws264
   default close-up camera renders black from inside Chapin).

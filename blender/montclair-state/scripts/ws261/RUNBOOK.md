# ws261 runbook (Fri Nov 27, 2026, 6:37 → ~7:15 AM ET) — Chapin S-drive N walk joints + UNIFY #32 lawn crease E of WS115 + #16 check + M2c grass-points review

Main before: ws260d (sha 60faaed0…). Backup montclair_state_pre_20261127ws261.blend = ws260d. Chain via `run261.sh` (= ws260/run260.sh, F261/P261/K261 grep tags; ws208/merge208.py, base meshes, ~1.7–1.9 GB):
ws260d + `f261a.py` → ws261a; + `f261b.py` (BND=bnd261e.json) → ws261b; + `f261b.py` (BND=bnd261f.json) → ws261c; + `f261c.py` → ws261d = MAIN (saved 6:47:52 AM ET, promoted 6:47:58 AM ET; sha261d.txt).
Rejected: ws261e = ws261c + f261b (THR=0.008, BND=bnd261g.json) + f261c — raised WS113 edge verts poke above the terrain → dashed shadow marks (renders/test/…0654…ws261e…).

1. `f261a.py`: WS261_WS129b_Chapin_S_drive_N_walk_sawcut_1p524m_UNVERIFIED — 20 cuts (2.34–2.40 m) every 1.524 m along the WS129b walk (PCA axis; f260d build). Base-mesh clip probe: nothing above the walk except the WS115/WS112 walk ends (≤ 1.3 cm, they lap over its W end).
2. `probe261b.py` (subset CHAIN via subrend234 + crop259, evaluated): same result on the evaluated scene (eval261b.json) — no terrain/lawn over the walk, strip or apron.
3. `probe261c.py`: UNIFY #16 — 0 Footpaths_OSM faces left in x −237…−230, y −237…−224; WS115/WS112/WS113 cover it (eval261c.json) → DONE (superseded).
4. `probe261d/e.py` (0.1 m evaluated grid): #32 crease = WS113 fan-fill NE edge 3–11.5 cm BELOW Terrain_LiDAR_DTM_1m along y −218…−208 (x −226…−218), plus a 5–15 cm lip the other way at y −206…−202. `bnd261.py` summarises WS113|Terrain neighbour steps.
5. `f261b.py`: feather WS113 base verts toward the evaluated terrain (median dz of boundary cells within 0.5 m, smoothstep over 1.5 m). Steps > 3 cm 177 → 76 → 25; max 0.152 → 0.050 m (probe261f/g). WS113_paving_edge_grade GN still runs after it; WS115 walk ≥ 1.7 m away (walk cell count unchanged).
6. `f261c.py`: WS261_UNIFY32_Chapin_W_wall_foot_pinhole_fill — 0.7 m quad at 122.60 (COLE_lawn_post2020_bs) over a 4-cell evaluated pinhole at (−216.4, −203.4) by the Chapin W wall foot (probe261h: 0 holes).
7. `probe261j.py` (1 cm transects): no gap at the boundary, heights match within 1–3 mm where sampled; `insp261k.py`: both sides COLE_lawn_post2020_bs, no steep faces, WS113 flat / terrain smooth shading.
8. `probe261i.py` (M2c review, library load from north/montclair_north.blend, NO SAVE): gd_grass_police_lawn_points (31,694 pts, GN gd_grass_lawn_instancer.002; x −352…−326, y −5…33): z − main top p5/p50/p95 −0.06/−0.01/+0.24, main has no grass objects there → MERGE candidate. gb_grass_slope_points (2,142 pts, GN cd_grass_instancer; x −333…−284, y −104…−84): p50 −0.42 m, 440/800 > 10 cm under main, 212/800 under WS74 cogen lot asphalt → DROP (main design wins).
9. WIPs `jobwip261.sh` (subrend234, terrain GN on, crop259, EXTRAJ extra261.json).

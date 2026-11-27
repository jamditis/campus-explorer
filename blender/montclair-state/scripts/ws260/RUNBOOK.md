# ws260 runbook (Fri Nov 27, 2026, 4:33 → ~5:1x AM ET) — UNIFY W64 bank W of the College Ave S-leg W walk + WS115 E-walk joints

Main before: ws259b (sha 5658f6ed…). Backup montclair_state_pre_20261127ws260.blend = ws259b. Chain via `run260.sh` (= ws259/run259.sh, F260/P260 grep tags; ws208/merge208.py, base meshes, ~1.9 GB):
ws259b + `f260c.py` → ws260c (promoted 4:52:51 AM ET); ws260c + `f260d.py` → ws260d = MAIN (saved 4:53:23 AM ET, promoted 4:54:21 AM ET; sha260d.txt).

1. `probe260a.py` (merge208 CHAIN, base meshes, no save, 8 s / 1.35 GB): per-object BVH rays on a 1 m grid x −268…−240, y −240…−194 → cov260a.json.
   Hole = between Panzer's S gym / E block and the WS103 walk / WS113 fan fill, y −238 … −205 (~500 m²). WS110 covers y ≤ −238.5, WS60 apron y ≥ −204.
2. 2020 NJ ortho crop (maps.nj.gov Orthos_Natural_2020_NJ_WM export, EPSG:3424; prep/ws259_w64/ortho260_grid.jpg, box only): a planted bank — grass with
   dark shrub masses and a bare tree, Panzer's shadow along the gym; pale paving at the Panzer E block foot (x −258…−252, y −212…−205).
3. `f260a.py` (→ ws260a, superseded): 0.5 m patch on the 2023 LiDAR (prep/ws259_w64/dtm259.npy) over the hole + 0.5 m overlap 4 cm under the neighbours,
   1.5 m blend to the neighbour edge height, 0.4 m down-skirts; Terrain material Ground_ortho_grass + 'ortho' UV (affine fit, resid 0); joined into
   Terrain_LiDAR_DTM_1m by GN WS260_W64_LiDAR_patch_join_terrain right after WS250_W63_LiDAR_patch_join_terrain (patch object render-hidden, as ws250).
4. `probe260b.py` / `probe260c.py` (subset CHAIN via subrend234 + crop259, exits before render; evaluated): remaining evaluated holes = a 0.5 m sliver S
   of the WS60 apron (y −204.5) and 2–3 cells at x −248, y −214 (WS113 fan fill missing there after its GN) → eval260c.json. (Use ≥ 60 ray steps: trees
   swallow 6.)
5. `f260b.py` (→ ws260b, superseded): + eval holes, box y −239…−203, shadow tint lum < 1.02 → ws247_lawn. Test: a 0.5 m hump over Panzer's E wall foot
   (blend/clamp used the WS60 apron's BASE top, higher than its evaluated surface) and the bluish Panzer shadow (lum ~1.0–1.6) still showed.
6. `f260c.py` (→ ws260c): WS60 excluded from blend/clamp (overlap under it = LiDAR − 4 cm); tint ramp ws247_lawn = clip((1.7 − lum)/0.6).
   Patch WS260_W64_CollegeAveS_W_bank_LiDAR2023_ground_patch: 2,793 verts / 2,456 faces (224 skirt quads), z 117.72 (skirt bottoms) … 120.87.
7. `f260d.py` (→ ws260d): WS260_WS115_E_walk_N_sawcut_1p524m_UNVERIFIED — f259b's build on WS115 (OSM 312849086; no modifiers): 22 cuts, 1.92–2.04 m.
8. WIPs `jobwip260.sh` (subrend234, terrain GN on, crop259; views 1–4 = W64, 5 = WS115 joints with EXTRAJ extra260.json).

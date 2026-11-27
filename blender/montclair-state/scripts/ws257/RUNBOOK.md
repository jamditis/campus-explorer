# ws257 runbook (Nov 26, 2026, 10:29 PM → ~11:45 PM ET) — saw-cut joints on the Feliciano E paving, M2c Maintenance Building, UNIFY #10 S edge

Main before: ws256d (sha f6d7de92…). Backup montclair_state_pre_20261126ws257.blend = ws256d. Chain (each via `run257.sh` = ws208/merge208.py CHAIN, base meshes, ~1.8 GB):
ws256d + `f257a.py` + `f257b.py` → ws257b; + `f257c.py` → ws257c (first strip, ridged) — superseded; ws257b + `f257c.py` (smoothed) → ws257d = MAIN.

1. `probe257a.py` (read-only): Feliciano E paving pieces (bbox, mats; no joints yet). `f257a.py` (W63k): WS257_W63k_Feliciano_E_walk_sawcut_joints_1p524m_UNVERIFIED —
   1.5 cm dark strips 3 mm proud, ray-draped on each piece's own flat top faces; transverse every 1.524 m (shared y grid), seam joint x −192.0,
   diagonal walk across its PCA axis, 4 × 4 grid on the SE pad. Plan check: `plot257.py` (dump, Blender) + `plotxy257.py` (PIL image).
2. `probe257b.py` (M2c queue vs main): Children's Center downpipes / valley flashing / ridge caps already in main (stale). `probe257c.py` / `probe257d.py`:
   Maintenance Building massing vs main structures + ground. OSM way 232850495 = building=university "Maintenance Building" (OSM API).
   `probe257e.py` → maint257.json (base drape targets; stays on the box). `f257b.py` merges it (bottom ring only lowered). Queue → `m2c_next257.json`.
3. UNIFY #10: `probe257f.py` (WS110 patch boundary vs whatever is outside, evaluated) and `probe257g.py` (skirt base vs evaluated vs patch along N–S lines):
   the 4 km skirt base mesh is up to 3.2 m below the patch's S edge (x −284…−172). `las257.py` (2023 J5D5 only reaches x −268) and `las257b.py`
   (2017 B17 J5D5/J5D6 fill E of it, overlap median shift −0.08 m) → prep/ws257_u10/dtm257.npy (box only). `probe257h.py` → edge257.json (patch edge + skirt
   profile per 1 m column; box only). `f257c.py` builds WS257_UNIFY10_S_edge_feather_DTM2023_to_skirt_UNVERIFIED. `probe257i.py`: ridge metric (2nd difference along x
   per row): ws257c p95 up to 0.28 m → ws257d ≤ 0.17 m (row 3) and ≤ 0.07 m beyond 6 m.
4. Renders: `jobwip257.sh` (subrend234 subset, terrain GN on) with `crop257.py` = crop256 run FIRST in the stack on world-space meshes > 50k verts
   (peak ~7.8 GB instead of > 8.4 GB). New objects are not in bbox205.json, so they come in through EXTRAJ (`extra257*.json`). The skirt is only in view 1/5 (extra257u.json).

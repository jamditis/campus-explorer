# ws268 runbook (Fri Nov 27, 2026, 8:34 → ~9:45 PM ET) — daily release model-20261127 + W72 College Ave / Lot 33 paving

Main before: ws267c (sha c9c37db6…). Backup montclair_state_pre_20261127ws268.blend = ws267c.

0. Pre-release check on ws267c: `m5wrap267.py` in the merge208 loader (see ws267 RUNBOOK) → m5check_ws267c.out: PASS
   (0 paths outside, 0 absolute, 0 missing, 0 unresolved libs; known 1 NaN helper, 3 empty GN carriers).
1. Release: `strip268.sh` (= ws256/strip256.sh with the date/paths changed, `mkdir -p` added; run with GATE=3300).
   strip244_lowmem removed 15 ortho/NAIP/LiDAR-raster images; ver244_lowmem: libs [] / unpacked []; 336,359,482 B,
   sha256 9034367d…91f5. Published as tag model-20261127 (asset + SHA256SUMS.txt); GitHub digest matches; staging .blend removed.
2. `probe268a.py` (= ws267 probe267a, box via BX=-385,-330,-50,-12; base meshes, no save) → ground = WS68 + M3b dtm_filled
   meshes with ortho drape; base-mesh hole x −357…−350, y −30…−50. `probe268b.py` lists every mesh in the box: no road / lot
   object S of the police at all. OSM (overpass, osm268 query): College Avenue 232850521, Lot 33 312848723, Carlisle Road 583841726.
3. `f268a.py` / `f268b.py` (first pass, ws268a/b, promoted 8:50 PM ET then REPLACED): built the paving but also pushed terrain base
   verts under it and feathered terrain down at the edges. Review: terrain is re-snapped by its GN modifiers (AGENTS.md rule 6: raise
   paving, never lower terrain) and the nearest-vertex edge fans left small cracks. Both dropped (not in the repo); main rebuilt from ws267c.
4. `f268c.py` (run268.sh, merge208 CHAIN, INF = montclair_state_pre_20261127ws268.blend = ws267c) → ws268c = MAIN (promoted 8:58:45 PM ET,
   sha 2f536070…): WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED. Ground sampled on the EVALUATED WS68 + M3b meshes (only their
   modifiers on; peak 1.9 GB); paving z = robust quadratic fit + smoothed positive lift + 4 cm, so it clears every ground sample
   (paving − ground min 0.04 m, p50 0.15 m); one constrained Delaunay triangulation of the polygon (no cracks), 21 faces under the
   police walk / terrace / deck / Maintenance Building dropped, 0.6 m edge skirt, Roads_OSM material. No terrain verts edited.
5. Pre-release check on ws268c: PASS (m5check_ws268c.out). WIPs: `jobwip268.sh` with
   `EXTRA="WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED"` (the new object is not in ws205/bbox205.json, so subset renders skip it
   without EXTRA), terrain GN on, crop259.

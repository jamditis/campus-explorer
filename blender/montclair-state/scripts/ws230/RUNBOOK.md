# ws230 runbook (Nov 19, 2026 ~5:30-~6:05 AM ET): W53j NE/E scene edge on USGS 3DEP 1 m (gap fill, strip + QI re-height, QJ ramp)
Main before: ws229d (f3be3cd0...). Main after: ws230d (promoted 5:53:50 AM ET, sha256 08c1c389836...). Interim mains ws230a
(5:41:53 AM, 1dbcfbb7...) and ws230b (5:45:04 AM, 4e1abb84...). Backup montclair_state_pre_20261119ws230.blend = ws229d.
Data: USGS 3DEP 1 m DEM (public TNM ImageServer exportImage, EPSG:3424, scene->state plane E = 575880 + x/0.3048006,
  N = 738340 + y/0.3048006): url_3dep1m_full.txt -> dep1m_full.tif -> dep1m_full_x-280_280_y-280_280_rowS.npy (row = y+280,
  col = x+280, 1 m). Check vs data/dtm_1m.npy: median diff 0.00, within ~0.1 m wherever dtm_1m is real (e.g. y 40 row).
  pad_mask230.npy = dtm_1m constant-run components >= 30 cells (padding detector; also flags flat building fills).
Probes (light: bpy.data.libraries.load of named objects only, no full open):
- probe230a/b: QI/QH/WS60 and base terrain verts vs dtm_1m and 3DEP (QI itself mostly on 3DEP; base terrain absent at x>230, y>50).
- probe230c: QI east boundary steps x 240 (y 28) -> 217 (y 248); WS60 inner edge at x 246 at padded dtm (+4..+8.5 m over 3DEP).
- probe230d: QJ_NE_seam_ramp = terrain z offset by the z of QJ_NE_seam_ramp_field (0..-1.81 m, x 212..240, y 160..240).
- probe230e/f: evaluated terrain + apron (+fill) top vs 3DEP on an 8 m grid x 214..250, y 30..246 (before: no ground at x 238..245
  for y > 46; after: within +-0.1 m except x ~220, y 174..210 = W53k).
- probe230g: which base mesh is on top at the residual spots. probe230h: Roads_OSM 0.75-1.3 m over 3DEP at x 212..230, y 170..215.
- probe230i: Q6 paving check (ground above Paths_Roads_OSM verts, x 150..280) - identical before/after ws230.
Build (memory-gated merge208 runner; run230.sh = run229.sh with the F230 tag):
  INF=<ws229d> OUTN=montclair_state_ws230a.blend CHAIN="ws230/fix230c.py ws230/fix230a.py ws230/fix230b.py" bash scripts/ws230/run230.sh
  INF=<ws230a> OUTN=montclair_state_ws230b.blend CHAIN="ws230/fix230d.py" bash scripts/ws230/run230.sh
  INF=<ws230b> OUTN=montclair_state_ws230d.blend CHAIN="ws230/fix230f.py" bash scripts/ws230/run230.sh
- fix230c: 1,163 QI verts (x>150) where dtm_1m is padded or >0.5 m off 3DEP and the vert >0.3 m off 3DEP -> 3DEP bilinear
  (670 lowered max 3.18, 493 raised max 6.43); 95 kept within 2 m of Paths_Roads_OSM paving.
- fix230a: gap cells = 1 m cells x 200..246, y -40..262 with no evaluated terrain, apron, or other visible Terrain-collection
  mesh (WN south-wood patch) at the centre (QJ_NE_seam_fill cells included, it sits 1.5 m under 3DEP): 3,464 cells, x 219..245,
  y -6..261. New WS230_NE_east_gap_fill_3DEP_UNVERIFIED (Ground_ortho_grass, ortho UVs): 260 verts = QI verts, 254 = apron edge,
  3,246 = 3DEP. WS60 strip verts x 246..268.5 with no terrain inside -> 3DEP (263 verts, max 8.51 m lowered, 0.99 raised).
  73 QI boundary verts > 0.3 m under 3DEP raised.
- fix230b: trees on the fill/strip re-seated: T_PinOak_L1_0400 +0.15, T_RedMaple_L1_0332 -0.05, T_SugarMaple_L1_0442 -2.71 m.
- fix230d: 5,777 QJ field verts (x >= 205, not within 2 m of paving) set to 0 offset (max -1.81 removed); 6,585 kept near paving.
- fix230f: remaining QJ field verts near the NE street zeroed where the highest un-ramped ground within 2 m (QI/QG/QH tops,
  else 3DEP) stays >= 5 cm under the lowest paving within 2 m (5,971 zeroed, 614 kept); street untouched (0.75-1.3 m over 3DEP).
  2020 ortho crop: url_ortho_NElot.txt / ortho_NElot_grid.jpg (2-lane street + sidewalk/verge, lot to the east).
- fix230e (REJECTED, not in main): W53m subdivide + tuck of WS60 under the SE street end; cut road-under-apron verts 20 -> 4 but
  opened a black hole in the close-up (renders/test/20261119-0548_ws230_test_W53m_SE_edge_road_closeup_ws230{b,c}_sub.jpg).
- jobtest230.sh (before/after), jobwip230.sh (four WIPs, subrend226, terrain GN on, EXTRA incl. the new fill object).

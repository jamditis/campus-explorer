# ws229 runbook (Nov 19, 2026 ~4:25-~5:00 AM ET): W53g QI patch band, W53e/W53f ortho UV registration, W53h south edge apron, W53i east apron strip
Main before: ws228f (1c3bd0a7...). Main after: ws229d (promoted 4:41:58 AM ET, sha256 f3be3cd0...). Superseded intermediate
mains: ws229b (4:32:29 AM, 796a3893...) and ws229c (4:36:03 AM, 19a0b0c5...). Backup montclair_state_pre_20261119ws229.blend = ws228f.
Build (memory-gated merge208 runner, all modifiers off at load, DNA-poke restore; run229.sh = run228.sh):
  INF=<ws228f> OUTN=montclair_state_ws229a.blend CHAIN="ws229/fix229a.py ws229/fix229b.py ws229/fix229c.py" bash scripts/ws229/run229.sh
  INF=<ws229a> OUTN=montclair_state_ws229b.blend CHAIN="ws229/fix229d.py" ...
  INF=<ws229b> OUTN=montclair_state_ws229c.blend CHAIN="ws229/fix229e.py" ...
  INF=<ws229c> OUTN=montclair_state_ws229d.blend CHAIN="ws229/fix229g.py" ...   (fix229f was a dry attempt; superseded by fix229g, not in main)
- probe229a: cumulative per-modifier ray heights at the residual SE samples -> the +2.25 m at (205,-45) appears with
  QI_east_edge_LiDAR_patch (it joins QI_east_edge_LiDAR_terrain_patch; ray-top wins).
- probe229b: that patch mesh vs dtm_1m / dsm_1m / 3DEP: its south band (y -60..-45) carries a blend to the old high base
  (e.g. (205,-45) 96.38 vs dtm 94.14, 3DEP 94.16, dsm 109.5 canopy).
- fix229a: 149 patch verts (x 86..246, y -60.5..-20) > 0.3 m over dtm_1m -> dtm_1m (mean 1.47, max 3.16 m; 3DEP also lower on 141).
- fix229b: 48 SE interior base-terrain verts > 0.3 m UNDER dtm_1m (faces < 25 m2) -> dtm_1m (mean 0.55, max 1.14 m).
- fix229c: fix228b re-run (trunk-ring tree re-seat): 1 tree.
- probe227a on ws229a: within 0.5 m 881 -> 891 of 902 hits; high 10 -> 7; low 11 -> 4. probe229c: the 11 left are on 2 m grid
  faces over real 1-2.7 m dtm steps (yard walls/terraces) = grid resolution limit.
- probe229d/f/g + fix229d (W53e/W53f): the grey sheet is Roads_OSM asphalt (a real street) under a mis-registered ortho drape.
  The terrain 'ortho' UV map is exactly u=x/500+0.5, v=y/500+0.5 elsewhere; in the SE quadrant (x>=25, y<=-25) it was off a
  median 8.6 m (max 45 m). 49,146 loops reset to the global map. Geometry untouched.
- probe229h + fix229e (W53h): south band = 3DEP skirt 0.4-1.2 m under the edge; new WS229_SE_south_edge_apron_UNVERIFIED
  (58 edge verts x 96.8..246.3 -> y -262, 171 faces, WS60 material + affine UV fit residual 0).
- probe229i/j/k + fix229g (W53i): WS60 apron north of A2 was 4 giant diagonal faces (16-19, ~1,200-1,460 m2) + a 1 m row at
  y -6..-5, standing 1.5-6 m over the LiDAR; deleted and rebuilt as a strip (rows every 4 m y -33.5..248, cols 246/253.5/261/
  268.5/276; inner = QI patch top, outer = skirt/far-field top + 2 cm; 284 faces, all facing up).
- W53j (open): dtm_1m is edge-padded north of y ~70 at x > ~225, the QI patch follows it (up to ~8 m over 3DEP).
- jobtest229.sh / jobtest229b.sh (before/after tests), jobwip229.sh (four WIPs, subrend226, terrain GN on).

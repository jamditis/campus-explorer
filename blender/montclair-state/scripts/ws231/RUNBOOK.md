# ws231 runbook (Nov 19, 2026 ~6:27-~7:10 AM ET; last session before 7 AM): E/NE/N scene edge paving vs ground, closed out
Main before: ws230d (08c1c389...). Main after: ws231b (see STATE.md / LOG.md for promote time + sha). Backup
montclair_state_pre_20261119ws231.blend = ws230d. No new objects (bbox205.json unchanged; pass WS226/WS229/WS230 objects via EXTRA).
KEY FINDING: Roads_OSM / Footpaths_OSM are GN-draped (OP/OO_redrape_LiDAR, QK_NE_end_drape, QO, WS57). Raw-vertex probes
(ws230 probe230h/probe230i) and subset renders WITHOUT KEEPMOD (subrend226 turns non-terrain modifiers off) show the
paving at its raw height, not where it renders. probe231b evaluates them: the NE street sits median +0.03 m on the ground
(the ws230 "0.75-1.3 m proud" was raw z). Use KEEPMOD="Roads_OSM Footpaths_OSM" for any paving test/WIP render.
Probes: probe231a (structure + raw heights; first run was killed by the watchdog at 0.67 GB free while the balloon was
  inflated), probe231b (evaluated paving vs evaluated ground + 3DEP; PF=<file>; boxes W53l/W53k/W53m, pit cells),
  probe231c/d (modifier node wiring; QK compares A = z - (max ground hit + offset) > 0.02 = a DOWNWARD drape),
  probe231e (QI patch north rows x 150..168, y 245..248 2.8-6.3 m under 3DEP), probe231f (WS60 y 248 duplicate low row).
Build (memory-gated merge208 runner, run231.sh = run230.sh with the F231 tag):
  INF=<main ws230d> OUTN=montclair_state_ws231a.blend CHAIN="ws231/fix231a.py" bash scripts/ws231/run231.sh
  INF=<ws231a>      OUTN=montclair_state_ws231b.blend CHAIN="ws231/fix231b.py" bash scripts/ws231/run231.sh
- fix231a: two RAISE-ONLY copies of QK_NE_end_drape_GN (Compare -> LESS_THAN -0.02), appended at the end of the stacks:
  WS231_NE_fill_drape (targets Terrain + WS230 fill + skirt, box x 195..250, y 135..258) on Roads_OSM (+0.03) and
  Footpaths_OSM (+0.05); WS231_N_woods_path_drape (Terrain + WS60 apron + skirt, box x 145..175, y 222..256) on
  Footpaths_OSM. QI patch verts x 150..168, y 245..248 (41, max 6.26 m) and 1 QG vert raised to 3DEP.
- fix231b: WS231_SE_end_apron_drape (Terrain + WS60 apron + skirt, box x 238..252, y -44..-14) on Roads_OSM (+0.03) = W53m.
  Its WS60 raise part was DROPPED (hidden duplicate low row; evaluated top unchanged).
Result (probe231b_after_b.out, evaluated): Roads W53k z-ground -0.02..+0.87 (was -2.73..+0.72), Footpaths W53k +0.03..+0.31
  (was -1.92), Footpaths W53l +0.04..+0.16 (was -6.23), Roads W53m on the apron +0.02..+0.14, QI pit cells 34 -> 0
  (12 left = WS60 apron ramp beyond the y 248 edge, by design).
jobwip231.sh: four views (subrend226, terrain GN on, KEEPMOD paving drapes on); D=test for before/after.

# ws232 runbook (Nov 19, 2026 7:33-~8:20 AM ET): W53b CELS/Calcia NE-corner walk overlays (north campus seam, first item)
Main before: ws231b (a0435be5...). Main after: ws232b (045ddbd5..., promoted 7:52:49 AM ET). Backup montclair_state_pre_20261119ws232.blend = ws231b.
FINDING (probe232a, EVALUATED, 2 m grid x 112..152, y 182..252, 756 samples): the top ground is ON USGS 3DEP 1 m (-0.37..+0.34 m,
median 0.00) and the live walks (Footpaths_OSM, OO/OP redrape GN) sit on it (median +0.05 m). The ws226 "walks 9 m under the terrain"
was the walk OVERLAYS only (OX_ scoring joints/lips/grime feather, OY_ panel tone + joints, PB2_ lawn fillet, OW3_ curb lip): they were
built on the raw pre-redrape walk heights (old padded dtm_1m ~128 m) and never followed the redrape, so they lay 5-10 m underground,
invisible. Decision: 3DEP is the ground (independent federal LiDAR; CELS podium base 137.2 m agrees); overlays follow the walks.
- fix232a (on ws231b -> ws232a): buried (>3 m) overlay verts; faces fully over paving lifted by (evaluated - raw walk z); other buried
  faces in the box deleted (over lawn, never visible). probe232d showed the dz lift left them -3..+1.1 m off the walks (the raw surface
  under them is not the one they were built on) -> superseded by fix232b.
- fix232b (ws232a -> ws232b): lifted verts SNAPPED to the evaluated Footpaths/Roads top at their xy + decal offset (tone 0.008,
  joints 0.012; targets from probe232e). OW3 curb lip + OX smoothed lip in the box removed (both objects now empty: they existed only
  here; a curb lip under a draped walk edge can't be placed from this data, UNVERIFIED).
Result (probe232d_ws232b.out): OX joints 3,236 / OY tone 28,278 / OY joints 2,376 verts at +0.01 m over the evaluated walks
(+0.03..+0.09 m over the ground).
Build: INF=<main> OUTN=montclair_state_ws232a.blend CHAIN="ws232/fix232a.py" bash scripts/ws232/run232.sh, then probe232e on ws232a,
  then INF=<ws232a> OUTN=montclair_state_ws232b.blend CHAIN="ws232/fix232b.py" bash scripts/ws232/run232.sh.
jobwip232.sh: four views (subrend226, terrain GN on, KEEPMOD paving drapes on); D=test ONLY=4 for the before close-up.

# ws228 runbook (Nov 19, 2026 ~3:32-~4:05 AM ET): W53d SE east edge + apex slivers + WS60 apron strip to the 1 m LiDAR
Main before: ws227g (5175f881...). Main after: ws228f (promoted 3:49:33 AM ET, sha256 1c3bd0a7...). Superseded intermediate
mains: ws228d (3:43:37 AM, d50d2e59...) and ws228e (3:46:52 AM, ffd766af...); both left a 2-3 m ridge/bank at the A1 corner.
Backup montclair_state_pre_20261119ws228.blend = ws227g.
Build = `INF=<ws227g> OUTN=<out> CHAIN="ws228/fix228a.py ws228/fix228c.py ws228/fix228d.py ws228/fix228e.py ws228/fix228b.py" bash scripts/ws228/run228.sh`
(run228.sh = run227.sh: memory-gated merge208 runner, all modifiers off at load, DNA-poke restore).
- fix228a: the SE terrain's east boundary was ONE 214 m edge A1 (246.29,-248.74; +3.57 m over dtm_1m) -> B (245.97,-35.0).
  The 1,545 faces with all verts in x>=230, -249<y<-34.9 are re-triangulated (CDT of their boundary edges; triangles kept
  where the old region covered them) with boundary verts every 2 m on that edge at dtm_1m and a 2 m interior grid at dtm_1m,
  blended to the old surface only within 4 m of the inner outline. A1 and A2 (245.97,-33.5; +1.75 m) snapped to dtm_1m. The
  coincident WS60 apron inner edge (runs A1 -> A2 directly; B is on it within 3 mm) is split at the same points.
- fix228c: snapping A1/A2 dragged the remaining long (up to 199 m) slivers incident to them under the DTM; region = faces
  incident to A1/A2 + their edge neighbours, re-triangulated the same way, mesh-boundary outline edges > 4 m split every 2 m at
  dtm_1m. The apron has only a LOOSE edge on the south line (no faces), so nothing there is split (pre-existing; UNVERIFIED gap).
- fix228d: lower-only: interior terrain verts in x 140..246, y -249..-33.6 with all linked faces < 25 m2 and > 0.3 m over
  dtm_1m set to dtm_1m (467 verts, mean 0.88 m, max 2.97 m) - the fix227x grid verts that were blended to the old slivers.
- fix228e: the apron's long column quads (x 246 -> 276) beyond that edge rebuilt as a grid (rows at every inner vertex,
  columns 253.5/261/268.5, outer edge unchanged/linear), heights linear from the terrain edge to the outer edge; UVs from an
  exact affine fit of the replaced faces (residual 0).
- fix228b: fix227b re-run (trunk-ring tree re-seat in the SE box): 21 trees, max |dz| 0.58 m.
- Face budget (SELF_REVIEW ws227 Q, probe228b per-modifier counts): final evaluated terrain 500,789 -> 507,251 faces
  (+1.3%); WS63 output 293,715 -> 300,177; VmHWM ~2.1 GB.
- Grid result (probe227a, 902 hits): within 0.5 m of dtm_1m 754 -> 881; >0.5 m high 140 -> 10 (max 3.74 -> 2.25 m, the 2.25
  m at (205,-45) is added by a terrain modifier: base 0.71); >0.5 m low 8 -> 11 (min -0.80 -> -0.96 m, interior slivers).
- Terrain/apron edge check (probe228h): 108 terrain edge verts, all matched by apron verts (xy within 1 cm, z within 2 cm).
- jobwip228.sh (TEST=1 for the before/after oblique; else the four WIPs).

# ws227 runbook (Nov 19, 2026 ~2:27-~3:10 AM ET): W53c SE corner terrain re-grid + W53d apex fan re-triangulation
Main before: ws226f (aace496b...). Main after: ws227g (promoted 2:43:43 AM ET, sha256 5175f881...). Intermediate mains: ws227a
(2:38:39 AM ET, e36d9399..., fix227a+b only, copy kept) and ws227f (2:41:40 AM ET, superseded: its east-edge taper left a
1 m wall, see fix227a). Backup montclair_state_pre_20261119ws227.blend = ws226f.
Each build = `INF=<in> OUTN=<out> CHAIN="ws227/fix227x.py ws227/fix227a.py ws227/fix227b.py" bash scripts/ws227/run227.sh`
(run227.sh = run226.sh: memory-gated merge208 runner, all modifiers off at load, DNA-poke restore). ws227g = ws226f + x + a + b.
- fix227x (W53d): the two base apex vertices on the mesh boundary, A1 (246.3,-248.7) +3.6 m and A2 (246.0,-33.5) +1.5-1.8 m
  over dtm_1m, carried fans of long slivers. Per apex: delete its fan faces (not the big triangle), keep the union outline,
  constrained-Delaunay re-triangulate with a 2 m interior grid at bilinear dtm_1m heights (blend back within 6 m of the outline
  and 12 m of the apex). The apices stay put (WS60 apron vertex coincides with each).
- fix227a (W53c): the SE base triangle (16,282 m2, centre ~(196,-137)) re-gridded the same way (2 m interior grid, 12 m taper
  from all three edges and the apices); its east edge (the mesh boundary at x~246) is split at the WS60 apron vertex on it (1).
- fix227b: trees (trunk-base ring, as fix226b) inside the triangle or the SE box x>95, y<-30 re-seated both ways to the
  evaluated terrain - 0.05 where it agrees with dtm_1m within 0.7 m (62 trees, |dz| <= 0.62 m).
- Rejected: fix227z (snap the two apices alone: slivers fell up to 3 m UNDER the DTM, ws227b) and fix227y (split long sliver
  edges: WS63_E_band_to_DTM subdivides every face > 20 m2 at level 6, so the terrain stack went to 8.6 M faces and the watchdog
  killed the merge, see probe227d). Big (>20 m2) SE base faces: 137 before, 10 after x+a (probe227e/f).
- Probes: probe227a (5 m grid of evaluated top terrain vs dtm_1m over x 140-245, y -250..-45, objects in the corner; TAG= names
  the json), b (which base face owns each residual high sample), c (WS60 apron vertices at the apices), d (per-modifier
  face counts + VmHWM), e/f (big-face counts). runp.sh = ws226 runp with ws227 paths.
- Grid result (924 samples, 22 no-hit; probe227a.json before, probe227a_g.json after): within 0.5 m of dtm_1m 338 -> 754;
  >0.5 m high 467 -> 140 (max 3.7 m, within ~12 m of the east edge/apices: W53d); >0.5 m low 97 -> 8 (min -0.8).
- jobtest227.sh (before/after oblique), jobwip227.sh (four WIPs).

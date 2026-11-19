# ws223 runbook (Nov 18, 2026 ~10:28-11:15 PM ET): W39 curb-return / Kasser landing corner (W44)
Main before: ws222i. Main after: ws223f. Fix chain (merge208, all modifiers off during the edit, raise-only / topology-only):
- ws223a: INF=main ws222i  CHAIN="ws223/fix223a.py"  (curb tops of WS220 return rings k16..k29 + WS27 curb_left rings 0-1
  RAISED 0.5-6.2 cm so the curb back sits 3 mm under the WS72 landing edge; profile now rises monotonically into curb_left ring 2)
- ws223b: INF=ws223a  CHAIN="ws223/fix223b.py"  (7 WS72 top faces with downward normals flipped; no vertex moves)
- ws223f: INF=ws223b  CHAIN="ws223/fix223d.py ws223/fix223f.py"  (fix223d: re-fill the ring fan v150 -> v260..v266 -> v152 by
  ear-clipping; fix223f: ROOT CAUSE of the white fold: WS72 quads (v130,v140,v142,v132) and (v140,v150,v152,v142) overlapped
  (v150 lies west of edge v140-v142, so the second quad was folded over the first); both re-filled as one simple polygon)
- REJECTED: fix223c (raise-only Laplacian of v152) made the folded quad steeper; dropped from the chain. fix223e (split the
  folded quad) superseded by fix223f.
Rebuild from scratch: CHAIN="ws223/fix223a.py ws223/fix223b.py ws223/fix223d.py ws223/fix223f.py" from ws222i.
Probes: runp.sh (modifiers off): probe223a (ring/landing verts), probe223b (lip along the curb back), probe223c/d (landing top
verts/faces), probe223e (stacked top faces by ray). probe223g = evaluated top-surface map, run as CHAIN inside subrend212.py:
  FILE=$PWD/montclair_state.blend CULL="-300,-220,-90,-20" CHAIN="ws223/probe223g.py" GRID="x0,x1,y0,y1,step" blender -b --python scripts/ws212/subrend212.py
Tests: t1.sh (F=..., TAG=...); WIPs: jobwip223.sh. No objects added (bbox205.json unchanged).
Residual: two thin wedge triangles (v150,v132,v140)/(v140,v132,v130) along the straight return segment slope 3 cm over ~3 cm
(landing edge ring is 2-4 cm above the landing interior f72); NE view: WS69 curb end / landing corner notch still open.
- REJECTED: fix223g (W45: subdivide the WS70 verge grass by the landing S edge so the WS72_KasserSW_walk_cut GN drops only
  verts under the slab). The evaluated map (probe223g, GRID -250,-248.3,-55.4,-54.3,0.1) got WORSE: a wider 125.67 band just
  outside the slab edge, so the trench is the cut GN reaching verts OUTSIDE the slab footprint, not long-triangle ramping.
  Next: read the cut GN ray direction/offset (Raycast + 'Math SUBTRACT 0.06' + 'MINIMUM') before touching the grass.

# ws222 runbook (main ws221c -> ws222a -> ws222b -> ws222c -> ws222d -> ws222e -> ws222g)
Merges use scripts/ws208/merge208.py via run222.sh (CHAIN env, OUTN output; INF = input file, default = current main).
- ws222a: CHAIN="ws222/fix222a.py"  (W41b: WS70 verge-grass verts under the WS72 Kasser landing footprint dropped to slab top - 4 cm;
  they sat at/above the slab top and showed through as a sawtooth triangle and a grass strip along the WS69 curb back)
- ws222b: INF=montclair_state_ws222a.blend CHAIN="ws222/fix222b.py"  (W42: asphalt verts of WS214 underfill / WS67 / KY lying under
  the WS72 landing or WS215 RHD SE sidewalk and above slab top - 2 cm set to slab top - 3 cm)
- ws222c: INF=montclair_state_ws222b.blend CHAIN="ws222/fix222c.py"  (W42: WS215 road-side top edge raised to the road + 5 mm,
  flush depressed-curb crossing; raise-only)
- ws222d: INF=montclair_state_ws222c.blend CHAIN="ws222/fix222d.py"  (W42: underfill v289 to 125.135 at the landing SW corner)
- ws222e: INF=montclair_state_ws222d.blend CHAIN="ws222/fix222e.py"  (W43: new WS222 gutter fill strip between the W39 return road
  face and the WS27 carriageway W edge)
- ws222f: INF=montclair_state_ws222e.blend CHAIN="ws222/fix222f.py"  (W43: WS72 landing S chord v150->v160 subdivided and moved
  onto the curb back of the return arc + curb_left start)
- ws222g: INF=montclair_state_ws222f.blend CHAIN="ws222/fix222g.py"  (triangulate the non-planar n-gons left by ws222f)
For a from-scratch rebuild, fix222a..g in that order reproduce ws222g (ws222e was built from main = ws222d).
Probes: runp.sh opens a file with every modifier off; probe222a-f/h/i print P222 lines. probe222g.py is run as a CHAIN inside
scripts/ws212/subrend212.py (terrain GN on, evaluated surface map, exits before rendering):
  FILE=$PWD/montclair_state.blend CULL="-300,-220,-90,-20" CHAIN="ws222/probe222g.py" GRID="x0,x1,y0,y1,step" blender -b --python scripts/ws212/subrend212.py
Tests: t1.sh; WIPs: jobwip222.sh. After adding objects, regenerate scripts/ws205/bbox205.json (bbox205.py) before subset renders.

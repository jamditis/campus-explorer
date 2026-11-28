# ws275 runbook (Sat Nov 28, 2026, ~1:50 → ~2:25 PM ET) — AGENTS.md rule 16 audit: no housing interiors in main or north

Session by lgn-cemain (fleet worker on Legion WSL) while Void is out of weekly usage. No model change: main stays ws274e.
Ask (#38 "start here", item 1): remove any housing interiors (rooms, labels, floor plans, corridors) from the main and north
files; the public dining floor of a dining hall in housing may stay.

1. Main file (ws274e as rebuilt on Legion), merge208-style loader, modifiers off, no save:
   - `probe275a.py`: text objects, and objects, collections and materials whose names say room, interior, floor plan, corridor,
     hallway, partition, label, bedroom, suite, dorm, stairwell or lounge; plus every object named for a housing building.
     29 text objects, all signs (CCOM, station, Montclair Heights). Every interior-named object, collection and material belongs
     to an academic building (CCOM newsroom, lounge and classrooms; CCM office; Café Diem; Richardson Hall's interior hint;
     the CCOM and CELS window-room shaders).
   - `probe275b.py` (`HOUS=housing275.json`: the 13 housing buildings in viewer/places.json, centre and radius, scene x = x,
     y = −z): every object whose bounding box lies inside a housing circle (+2 m). Blanton 28, Bohn 54, Freeman 453, Russ 27,
     Stone 51, Webster 5, Children's Center 24 objects; the north halls (Basie, Paul, Sinatra, Hawk Crossings) have none in main.
     All are facade, roof, step, planting and tree parts. Freeman's VC "glass backplanes" are dark planes behind the glass.
2. North file: frozen until Void returns, so checked on the published tiles instead (models/main at 83be40e):
   - `glbnames275.py`: node, mesh and material names in every n_ tile. Only University Hall's UH_win_room_* window shader
     (academic) and a station stair.
   - `house16.mjs` (run from /workspace/nj-scenes/web/tools for gltf-transform and the meshopt decoder; tiles at 2b87835):
     every vertex of every t_, n_t_ and sw_t_ tile inside a housing outline, by building and material. Outlines: each housing
     place in viewer/places.json as its full circle + 2 m, and each ring in blender/scripted/village/v_buildings.json (Hawk
     Crossings, Fenwick, Williams, Paul, Basie and the rest of the Village). Inside the housing outlines: brick, trim, roof,
     glass, lawn, paving and tree materials only.
   - Stone Hall's circle (r + 2 m = 50.9 m) reaches Richardson Hall's glass tower in t_0_1: QU_int_* (blinds, ceiling panels,
     carpet, terrazzo, partitions, walls) and QU_kit lounge seating. QU is Richardson's prefix (QU_Richardson_interior_hint;
     academic, OSM way 313027426, 68 m from Stone Hall's centre).
3. Result: no housing interiors in the main file or in any published tile; nothing removed. OPEN: the north source .blend itself
   (frozen while Void is away). The tiles leave out hidden-render objects and types outside the export set, so the north file
   needs its own name and footprint probe (probe275a/b with INF on montclair_north.blend) before this row closes. The rough interiors in the
   scripted areas (Balance Kitchen at Freeman, Sam's Place) are the dining-floor exception and belong to blender/scripted.

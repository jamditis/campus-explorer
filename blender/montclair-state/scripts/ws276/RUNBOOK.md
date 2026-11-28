# ws276 runbook (Sat Nov 28, 2026, ~2:20 → ~3:10 PM ET) — Sprague Library east doorway for the rough interiors

Session by lgn-cemain (fleet worker on Legion WSL) while Void is out of weekly usage; same tools and file layout as Void's.
Main before: ws274e as rebuilt on Legion (release model-20261127 + ws268c…ws274e replayed with each session's own scripts; every
RUNBOOK figure reproduced, e.g. ws274 105 curb rows / 1 raycast miss, ws272 258 verts / max lower 4.08 m; sha256 eb44b888…, a
Blender save is not byte-identical to Void's 25675b66…). Backup montclair_state_pre_20261128ws276.blend = that file.
On Legion every Blender job on the main file runs in its own memory unit (`systemd-run … -p MemoryMax=10G`, see run276.sh): the
worker's own 4 GB unit OOM-killed Blender on the main file. Start jobs from a script file: the render gate in ws263/srun263.sh
(`pgrep -f "subrend|cutrend|render" | grep blender`) also matches a shell whose command line names both words, and waits on it.

1. Ask: ofj-ceinteriors' door list (officejawn, ofj-ceinteriors data/door-list.md, Nov 28): Sprague Library door 1, centre
   (−50.20, 34.99) on the published shell's outer face, sill 137.90 m, 2.0 × 2.4 m, facing 103°; evidence the library main-level
   map (inside.montclair.edu). Its note asked whether the 'Sprague Library L0' bounds reaching x −42.8 mean a separate east wing.
2. Probes (no save): `probe276a.py` (objects in x −60…−36, y 24…46 and their x-facing faces on the door line) and `probe276b.py`
   (section at z 139.0).
   - No separate wing. The L0 east face runs on a 13° bearing (outward normal 103°, the door's facing), so it reaches x −42.8 only
     at its N end (y 77). At y 31.8…35.2 it is brick at x ≈ −51.1…−50.4: the door centre is 0.2 m outside it.
   - At the door: a 0.6 m deep recess in L0, y 33.4…35.7, z 138.8…140.7 (the grey panel south of Café Diem in the eye shots). It
     is untextured: its faces carry the brick material with no brick mapping.
   - N of the recess corner (−50.28, 35.57) L0 is the hidden Café Diem strip (North_CafeDiem_L0hide_bt): the café glass stands
     2.5 m behind it. The door's north 0.45 m falls in that strip.
   - The stucco 'Sprague Library walls' are hide_render (not exported). The Café Diem patio pavers, joints and curb reach up to
     the threshold (they print as "other mesh in opening"); no change to them.
3. `f276a.py` (run276.sh = merge208 CHAIN, on ws274e) → ws276a (saved 2:37:31 PM ET, promoted 2:40 PM ET, sha256 512ab107…20ff).
   - EXACT boolean (hole tolerant) of a box from 0.5 m outside the face to 1.2 m inside it, past the recess back. The faces the
     box leaves on its back plane (2 faces, 4.80 m² = the opening) are deleted, so the opening reaches the plan's lining instead
     of ending in a niche.
   - Every L0 vertex outside the box is unchanged (checked). 658 → 675 verts, 439 → 450 faces.
   - Jambs and head get the brick material, the threshold the patio precast. Reveal faces in the hidden café strip get the hide
     material, or the north jamb stands as a fin in front of the café glass.
   - Brick mapping fitted on the L0 front faces at the door (12 loops, max residual 0.0001), then applied on each face's own
     plane to the 10 non-front brick faces round the door (the new reveals and the old recess).
3b. `f276b.py` (run276.sh with CHAIN=ws276/f276b.py OUTN=ws276b.blend, on ws276a) → ws276b = MAIN (saved 3:05:58 PM ET,
   promoted 3:06:07 PM ET, sha256 86706c73…7606). Codex review P2: the first t_-1_0 export darkened the Sprague roof.
   - The release copy (ws244/strip244_lowmem.py) drops ortho images and feeds each such material a stand-in RGB node.
   - On 'North_roof_ortho2020.002' (Sprague L0, L1 main, SW raised block) that stand-in is the default (0.20, 0.20, 0.18) at
     HSV value 0.6, so the export flattened the roof to 0.20 grey.
   - The published t_-1_0 (ws251b, Void's file with the ortho image) has (0.4595, 0.4755, 0.4271) at HSV value 0.95. f276b sets
     the RGB node and the value to that.
   - Any tile exported from a release-derived file can drift the same way. Before publishing, compare it with the published tile
     (`colcmp276.mjs`). t_-1_0 after ws276b: 258 of 258 materials same colour.
   - run276.sh now fails unless Blender exits 0 and SAVED prints, and removes the output first (Codex review P2). A CHAIN naming a
     missing script exits 1 and leaves no file.
4. Renders (`cams276.sh`, subrend234 + crop259; before on ws274e, after on ws276a): eye from E, eye from SE, closeup. The recess
   head above the door (140.3…140.7) keeps a small untextured sliver.
5. Tiles: chunk plan on this file (34 chunks; Sprague is in t_-1_0), then, after #136 (tiles committed whole with
   models/main/sources.json; lod, tex, geo and manifest built by site.sh), `SCENE=main SKIP_PLAN=1 ONLY=t_-1_0 build_web.sh`
   on the current main (ws277b; t_-1_0 is the same as in ws276b, Alumni House is in t_-3_-2).
   - t_-1_0 11,267,332 → 11,215,464 B (whole tile), 2,216,273 → 2,217,627 triangles.
     - Sprague brick +21 triangles: the reveal.
     - The rest are ws252…ws274 changes inside the tile: the published main tiles came from ws251b.
     - Linked-library materials carry a .001 suffix since the release file made them local (same triangles; the viewer matches
       names by prefix only).
   - Colours: 258 of 258 materials match the published tile (`colcmp276.mjs`), after ws276b.
   - sources.json main label: "ws251b; t_-1_0 from ws277b".
   - Paint layers kept as published. paint.py rebuilds paint.json from the raw sidecars of this run only, so a one-tile run on a
     machine without a full build's raw folder would drop every layer. Restored from main.
6. Not done: a full main re-export (needs the ws211…ws221 paint mask tile lists, which live only on Void's box); the other 13 doors
   wait for #125.

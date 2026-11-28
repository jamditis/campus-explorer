# ws277 runbook (Sat Nov 28, 2026, ~3:00 → ~3:40 PM ET) — Alumni House (OSM way 232846660) as LiDAR context massing

Session by lgn-cemain (fleet worker on Legion WSL) while Void is out of weekly usage. Main before: ws276b (sha 86706c73…).
Backup montclair_state_pre_20261128ws277.blend = ws276b. Ask: #38 start-here item 3 (university property, about x −359,
y −272, in the row-78 strip S of Normal Ave W, which ws173 left without houses under BOUNDARY).

1. Evidence (data outside the repo, /workspace/data/alumni from tools/evidence/fetch.py; nothing committed):
   - OSM outline, 8 corners, x −365.4…−353.3, y −279.2…−265.1, rotated about 11°.
   - NJ 2020 ortho (0.1 m): a dark grey shingle hip roof on the main block and a gabled S wing, matching the outline.
     Mid-band roof colour inside the outline sRGB (0.24, 0.28, 0.28).
   - 3DEP 2014 points: no class 6 here.
     - Ground 114.7 m (p50 of class 2 within 6 m).
     - Main block roof cells 6–8 m above ground: ridge about 122.7 m, running along the long side.
     - No returns over the S wing (scan gap y −272…−275); trees about 20 m tall to the S.
   - No public photo of the house found (web search, Nov 28), so the wall colour is a guess.
2. `probe277a.py` (no save): objects round the house.
   - Void's row-78 pieces start at x −346 (WS172 front-yard lawn) and x −348.5 (WS173 driveway D1). The WS163 Normal Ave layer
     ends at x −348. The house (max x −353.3) touches none of them and stands on the context skirt.
3. `f277a.py` (run277.sh, merge208 CHAIN, on ws276b) → ws277a = MAIN (saved 3:15:27 PM ET, promoted 3:29:27 PM ET, sha256
   edd81f35…8386). The house is one object, `WS277_Alumni_House_OSM232846660_LiDAR_massing_UNVERIFIED`, 28 verts, 17 faces:
   - Walls on the OSM outline from 113.9 (0.8 m under grade) to eave 119.9 (UNVERIFIED), closed by a flat cap.
   - A hip roof on the main block's rectangle (a 0…11.0 m, b 0…6.5 m) to 122.7.
   - A gable on the S wing (a 7.5…11.0, b 6.5…12.2) to 121.5 (UNVERIFIED, no returns).
   - Materials: WS277_house_wall_cream_UNVERIFIED and WS277_house_roof_shingle_ortho2020_UNVERIFIED (0.07, 0.08, 0.08).
   - f277a prints the WS172 and WS173 west edges as a check: both stay clear.
3b. Codex review (one pass, 2 × P2): the ~5.5 × 2.2 m connector between the main block and the wing (OSM corners 2…4) had
   only the flat cap; run277.sh's usage line named run276.sh. f277a now adds a connector roof, hipped at its W end, ridge along
   the long side at 45° (121.0), run 0.5 m into the wing gable; usage line fixed. Rerun on the backup (ws276b) → ws277b = MAIN
   (saved 3:33:08 PM ET, promoted 3:33:15 PM ET, sha256 118867a5…de03): 34 verts, 21 faces.
4. Renders (`cams277.sh`; before on ws276b, after on ws277a): eye from Normal Ave NE, oblique from NE.
   - ws205/bbox205.json had to be rebuilt on ws277a (`BBF=ws277a.blend`): subset renders only append objects listed in it.
   - Start render jobs from a script file. A shell whose command line names both "render" and "blender" blocks srun263's gate.
5. Tiles: chunk plan rebuilt on ws277a (34 chunks), then (after #136, whole tiles + sources.json)
   `SCENE=main SKIP_PLAN=1 ONLY=t_-3_-2 build_web.sh` on ws277b.
   - t_-3_-2: 721,312 → 718,012 B, 232,100 → 232,140 triangles (+40, the house), 2 new materials. The other 35 materials keep
     their published colours (ws276/colcmp276.mjs).
   - Paint layers kept as published. sources.json main label "ws251b; t_-1_0 and t_-3_-2 from ws277b".

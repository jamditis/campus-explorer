# ws269 runbook (Fri Nov 27, 2026, 10:33 → ~11:30 PM ET) — W72b College Ave / Lot 33 paint, tree island, island tree

Main before: ws268c (sha 2f536070…). Backup montclair_state_pre_20261127ws269.blend = ws268c.

1. Ortho: NJ 2020 Natural WMS (img.nj.gov, EPSG:3424, scene -> state plane E = 575880 + x/0.3048006, N = 738340 + y/0.3048006),
   url269.txt, x −398…−302, y −68…−12 at 0.1 m/px (ortho269.png, not in the repo).
2. `paint269.py`: top-hat bright, low-saturation, thin components inside the ws268 polygon (eroded 0.6 m) -> PCA line segments
   (41); car-glare, tree, turn-arrow boxes dropped -> paint269k.json (31 strokes + the island axis picked by eye from a luminance
   profile of the dark band: (−357.5,−36.6)->(−334.5,−40.9), 2.6 m wide). The dark-component pass in paint269.py only found cars
   and the Maintenance Building shadow (not used).
3. `f269a.py` (run269.sh, merge208 CHAIN, INF = main ws268c) -> ws269a = MAIN (saved 10:38:38 PM ET, promoted 10:44:51 PM ET):
   - WS269_W72b_CollegeAve_Lot33_paint_ortho2020_UNVERIFIED: 30 strips (1 skipped, off the paving), +1.2 cm on the WS268 paving top
     (base-mesh raycast), material es_rhd_stall_paint_worn.
   - WS269_W72b_Lot33_tree_island_curb_ortho2020_UNVERIFIED (15 cm curb, 0.15 m wide, outer face 0.25 m deep) and
     WS269_W72b_Lot33_tree_island_mulch_UNVERIFIED (5 cm under the curb top); both follow the paving (z 119.31…121.11 along the island).
   - WS269_tree_Lot33_island_ortho2020_h13m_UNVERIFIEDspecies: linked duplicate of the WS165 red maple, scaled 13/18, trunk at
     (−347.5, −38.4) under the ortho crown (~11 m across).
   No terrain or paving vertices edited.
4. WIPs: `jobwip269.sh` with `source cams269.sh` (EXTRA lists the paving + the four new objects; they are not in ws205/bbox205.json).
5. `las269.py` (geo venv with laspy; 2023 J5D6 + J5D5 tiles, x −362…−305, y −60…−25): class-1 canopy W of x −335 peaks at 11.9 m
   over ground at (−349.5, −36.5), crown x −354…−347, y −34…−44; a second, larger canopy x −324…−305, y −40…−60 (S of the road, E end of
   the lot; not built — no island visible under it in the ortho).
6. `f269b.py` (run269.sh on ws269a) -> ws269b = MAIN (saved 10:50:31 PM ET, promoted 10:50:40 PM ET): island tree moved onto the LiDAR
   crown, trunk (−350.0, −38.0) on the island axis, 12 m; renamed WS269_tree_Lot33_island_LiDAR2023_h12m_UNVERIFIEDspecies.
   WIPs re-rendered from ws269b (cams269.sh EXTRA updated to the new name).

# ws236 runbook (Nov 19, 2026, 11:31 AM–12:2x PM ET) — UNIFY W53q (M3b corridor ↔ main-native ground seams)

Main before: ws235b (sha abb9a7d1…). Main after: ws236c, promoted 11:54:05 AM ET (sha cd1febbb…). Backup montclair_state_pre_20261119ws236.blend = ws235b. Interim ws236b was main 11:40:26–11:54:05 AM (sha 78a6834b…).

Evidence call per edge: M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam is the north 1 m LiDAR DTM. PK_Feliciano_west_DTM_fill_UNVERIFIED is a synthetic fill (no modifiers), WS60_terrain_edge_apron_LiDAR_to_skirt is a LiDAR-to-skirt feather, and WS68_RHD_ground_northDTM's W/S/N edges were feathered over 8 m into the skirt/apron (ws68). So the synthetic side moves toward the LiDAR; M3b and all fine-tuned interiors stay.

1. `probe236a.py` (read-only): modifiers on the edge objects (PK none; WS60 2 GN; WS68 1 GN; M3b none; ballast none).
2. `CHAIN="ws236/f236a.py" OUTN=montclair_state_ws236a.blend bash scripts/ws236/run236.sh` — PK + WS60: seam = boundary verts within 3 m of an M3b boundary vert; dz = IDW(3) M3b boundary z − vert z; every vert within FD=12 m of the seam gets smoothstep(1 − d/FD)·IDW(4) dz. Skipped where any other object's geometry lies within 1.5 m (2D) and −1…+3 m vertically (19 PK verts by Ballast 0 / rail ties). PK 3258 moved (max 4.83 m), WS60 63 (max 3.15 m).
3. `FT=WS68_RHD_ground_northDTM FD=8 CHAIN="ws236/f236b.py" INF=…ws236a.blend OUTN=montclair_state_ws236b.blend` — same on WS68's west edge (1097 moved, max 5.03 m; 23 blocked by fu_deck_base_strip).
4. `probe236g.py` / `probe236g_b.py` (= probe235g on ws236a/b): seam step medians −1.9…+2.0 m → −0.01…+0.01 m.
5. `probe236c.py` (FILES="ws235b ws236b"): object verts under the three grounds in x −450…−200, y −140…290 — 9683 before, 9683 after (all pre-existing deck-structure verts under ground; 0 new).
6. `CHAIN="ws236/f236c.py" INF=…ws236b.blend OUTN=montclair_state_ws236c.blend` — the WIP oblique still showed a dark line along the seam: the grounds stop 1–3.6 m short of M3b (M3b was cut to never stack on them), so the skirt (held 0.35 m under) showed through. Each seam boundary edge extruded to the nearest M3b boundary + 0.6 m overlap, new verts at M3b − 0.04 m (PK 290 faces, WS60 26, WS68 135), UVs copied from the source vertex, dominant material.
7. `probe236e.py` (evaluated, skirt GN on): top surface along the close-up line = M3b then PK fill (no skirt).
8. WIPs: `bash scripts/ws236/jobwip236.sh` (subrend234 + extra235.json; skirt, M3b, WS60 in KEEPMOD).

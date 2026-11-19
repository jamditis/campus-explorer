# ws234 runbook (Nov 19, 2026, 9:27–10:0x AM ET) — ONE-SCENE M2b + M3a

Main before: ws233d (sha 156282f5…). Main after: ws234e, promoted 9:45:06 AM ET (sha 0478f2fc…).

1. `probe234a.py` (read-only, north file): visibility census of the station/rail batch → `m2b_vis234.json` (16 hidden north objects are skipped).
2. `CHAIN="ws234/m2b234.py" OUTN=montclair_state_ws234a.blend bash scripts/ws234/run234.sh` — M2b: 148 objects appended into NORTH_MERGE/N_station_rail, 9 train parts linked from assets/njt_trains.blend inside their instanced collections. Refuses University Hall, main itself and sprague_cafe_src.
3. `probe234b.py` — raw seat probe (bottom verts vs main ground). Showed the batch sitting on the 40 m 3DEP skirt.
4. `CHAIN="ws234/m3a234.py" INF=…ws234a.blend OUTN=montclair_state_ws234b.blend` — M3a: north 1 m LiDAR DTM appended as one object, faces kept only where every vertex has y >= 515 (main-native content ends at y 509); skirt base verts lowered 0.35 m under it.
5. `CHAIN="ws234/m3a234c.py" INF=…ws234b.blend OUTN=montclair_state_ws234c.blend` — delete skirt faces fully inside the extension.
6. `CHAIN="ws234/m3a234g.py" INF=…ws234c.blend OUTN=montclair_state_ws234e.blend` — GN modifier `WS234_skirt_under_M3a_ext` at the end of the skirt stack holds the evaluated skirt 0.35 m under the extension.
7. `probe234e.py` / `probe234f.py` — evaluated checks (seat per 50 m band; skirt-over-extension on a 5 m grid: 566 → 113 of 3442 points, max 2.29 m).
8. WIPs: `bash scripts/ws234/jobwip234.sh` (subrend234 = subrend226 + `EXTRAJ` JSON name list for names with spaces + dedupe; skirt in KEEPMOD so its GN runs).

Rejected: `M3A_RULE=v2` (ws234d) — west rail corridor slice; its edge ran along the rail so the straddling skirt faces still covered the cut. Left for M3b.

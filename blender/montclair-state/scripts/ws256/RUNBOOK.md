# ws256 runbook (Nov 26, 2026, 8:38 → ~9:3x PM ET) — daily release model-20261126 + W63h/i/j Feliciano E walk ↔ OSM path junction + M2c police south walk

Main before: ws255d (sha 6af9b321…). Backup montclair_state_pre_20261126ws256.blend = ws255d. MAIN = ws256d (saved 9:05:43 PM ET, promoted 9:06:30 PM ET, sha f6d7de92…; sha256d.txt). Chain: ws255d + `f256a.py` + `f256b.py` → ws256b; + `f256c.py` → ws256c; + `f256d.py` → ws256d (each via `run256.sh` = merge208 CHAIN, base meshes, ~1.9 GB).

1. Release: `GATE=3300 bash scripts/ws256/strip256.sh` (= ws244 strip244.sh with the date/paths changed and a GATE env for the start gate) → exports/model-20261126/montclair_state_20261126.blend (336,778,635 B, sha 90b907f7…), verified libs [] / unpacked []. `gh release create model-20261126 … --notes-file NOTES.md <blend> SHA256SUMS.txt`, digest compared.
2. `probe256a.py` / `probe256b.py` (read-only, evaluated): Footpaths_OSM at the junction is smooth (8 % cross-fall over the LiDAR swale); ws255 paving N end 138.96–138.99 vs the ws254 extension 138.78 = the fold.
3. `f256a.py` (W63h): paving + extension N 2.5 m blended to the path's profile at y 191 (table FPX/FPZ from probe256b); extension sliced along x first. `probe256c.py`: who is on top (terrain-over-paving count 0).
4. `f256b.py` (W63i): ws247_lawn tint on the ortho shadow E of the walk, S of the path (material attribute only).
5. `rev256.py` + `probe256d.py` (M2c police walk, read-only, north ground patches loaded) → `police_walk256.json` (drape targets + faces under blockers); `f256c.py` appends ge_police_south_walk from north/montclair_north.blend, deletes those faces, drapes it. Queue → `m2c_next256.json`.
6. `f256d.py` (W63j): lawn along the extension's E edge raised (raise-only ≤ 0.25 m); `probe256e.py` edge vs lawn.
7. Renders: `jobwip256.sh` (subrend234 subset, terrain GN on; ONLY=1..6; views 5/6 = police with EXTRAJ extra256.json + ws239/upd239.py). `crop256.py` = optional render-only GN crop for meshes > 200k verts (memory); subset renders peak ~8.4 GB VmHWM, so wait for ≥ 10 GB MemAvailable or accept a tight watchdog (WDM 1300).
8. `police_walk256.json` (per-vertex drape targets) stays on the box; regenerate it with `probe256d.py` before re-running `f256c.py`.

# ws244 runbook (Nov 25, 2026, 8:28–~9:15 PM ET) — daily release model-20261125 + W62 east-bank edge

Main before: ws243c (sha 32d7ecad…). Backup montclair_state_pre_20261125ws244.blend = ws243c. Copy ws244a = MAIN (promoted 8:39:11 PM ET, sha f755f1c2…, see sha244.txt).

1. Release (low memory): `bash scripts/ws244/strip244.sh` runs `strip244_lowmem.py` (strip215 without its own save) as a merge208 CHAIN on the main IN PLACE (a copied .blend loses its relative library paths), saves exports/model-20261125/montclair_state_20261125.blend compressed (peak ~2 GB). Verify with `F=<file> blender -b --factory-startup --python scripts/ws244/ver244_lowmem.py` (libs [] and unpacked [] required; the plain ver215 full-eval open gets watchdog-killed when the balloon is up). Then `gh release create <tag> -R jamditis/campus-explorer --notes-file NOTES.md <blend> SHA256SUMS.txt` and compare the asset digest.
2. `f244a.py` (→ ws244a): grow WS243_stands_pitch_holdunder_target 1.5 m outward from every boundary edge, flat at edge height; skip a strip where a lower target part lies under it. Run: `GATE=3000 CHAIN=ws244/f244a.py OUTN=montclair_state_ws244a.blend bash scripts/ws244/run244.sh`.
3. `probe244a.py` (= probe243b, evaluated seat check): `C=-420,-200,-60,220 F=montclair_state_ws244a.blend bash scripts/ws244/jobprobe244.sh`. turf 19 → 0, E walkway 19 → 5, fence posts 30 → 8, E pad 72 → 59 (NE corner ≤ 1.11 m open).
4. `probe244b.py` sky-speck ray check from the eye-WIP camera (`C=-360,-200,20,180 CH=ws244/probe244b.py`): hits = Roof_vent / roof exhaust hoods of a culled building → subset artifact.
5. WIPs: `GATE=3000 bash scripts/ws244/jobwip244.sh` (EXTRAJ = ws243/extra243.json; close-up camera = E bank edge from the W).

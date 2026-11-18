# ws219 runbook (main ws218b -> ws219a -> ws219c -> ws219d -> ws219e)
Merges use scripts/ws208/merge208.py via run219.sh (CHAIN env, OUTN output), from the then-current main:
- ws219a: CHAIN="ws219/fix219a.py"  (WS69 curb depressed at the RHD SE crosswalk: bisect + 1.5 m taper)
- ws219c: CHAIN="ws219/fix219b.py ws219/fix219c.py"  (WS67 asphalt -> KY material; ws214 curb-return nose tucked under the walks)
- ws219d: python3 mkmask219.py (needs cw219.json from dump219.py), CHAIN="ws219/fix219d.py"  (RHD SE crosswalk bars -> KY paint mask)
- ws219e: python3 mkmask219b.py (needs paint219.json from dump219b.py), CHAIN="ws219/fix219e.py"  (WS179/WS130/WS135a/WS138a paint -> WS27 asphalt masks)
Mask PNGs are written to montclair-state/data/ (derived from model geometry; not committed).

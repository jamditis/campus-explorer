# ws220 runbook (main ws219e -> ws220a -> ws220b)
Merges use scripts/ws208/merge208.py via run220.sh (CHAIN env, OUTN output; INF = input file), from the then-current main:
- ws220a: ./runp.sh dump220.py (writes paint220.json; worn-white colour set to 0.70/0.70/0.68), python3 mkmask220.py,
  CHAIN="ws220/fix220a.py"  (SF_Lot38 draped stall stripes -> world-XY paint mask in SF_asphalt_worn_UNVERIFIED; draped object deleted)
- ws220b: INF=montclair_state_ws220a.blend CHAIN="ws220/fix220b.py"  (College Ave curb jog E of the RHD SE / Kasser landing:
  new curb return WS220_CollegeAve_curb_jog_return_UNVERIFIED joining the WS69 N gap-strip curb end to the WS27 curb_left W end,
  WS72 landing edge pulled behind the curb back line, WS70 grass behind the curb raised to curb top - 3 cm)
Probes: runp.sh opens main with every modifier off (no full-scene eval); eprobe220*.py run inside a subset render
(srun CHAIN) for evaluated top-down ray grids (PG="x0,x1,y0,y1,step"), then exit before rendering.
Mask PNGs are written to montclair-state/data/ (derived from model geometry; not committed).

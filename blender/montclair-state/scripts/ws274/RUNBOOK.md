# ws274 runbook (Sat Nov 28, 2026, ~8:30 → ~9:20 AM ET) — W72e College Ave N curb + gutter, turn arrow, yellow hatch

Main before: ws273c (sha 93a53533…). Backup montclair_state_pre_20261128ws274.blend = ws273c.
First session of the Nov 28 building day: College Ave / Lot 33 finish.

1. Evidence: NJ 2020 0.1 m ortho (scripts/ws269/url269.txt; crops not committed).
   - N edge of College Ave: a light concrete band along the paving's N outline (y ≈ −19.3…−21) for x ≈ −385…−337 (curb line + walk
     along the police-lawn foot; parking bay in front of the police building).
   - Westbound approach to Carlisle Rd: stop bar at x ≈ −382 and two bright blobs E of it at (−379.5, −20.2) and (−380, −23),
     read as one left-turn arrow (stem W, head S). Arrow TYPE UNVERIFIED (blurred at 0.1 m).
   - E end of the parking bay by the red-roof building: hatched box x −338.6…−334.4, y −25.4…−28.3 with 45° stripes. Top-15 %
     pixel colour (182,190,161) is yellower than the white arrows (191,201,183) and centre dashes (178,190,171) → faded yellow,
     colour UNVERIFIED.
2. `f274a.py` (run274.sh = merge208 CHAIN, on ws273c) → ws274a (test only): curb along the WS268 paving N outline x −384…−337,
   sampled every 0.5 m (max y of the top outline per x), Gaussian-smoothed (σ 1.2 m). Curb face 0.15 m inside the outline,
   15 cm reveal, 15 cm top, back face 0.40 m deep; gutter pan 0.45 m in front of the face, +6 mm over the asphalt, 2 mm dished.
   Raycast on the paving top only; no paving or terrain vertices edited (AGENTS.md rule 6). First pass used the tan OQ paving tone
   and clamped the line to the outline, which kept a 1 m jog at the police S walk end (renders/test/20261128-0832_…ws274a…).
3. `mkmask274.py`: redraws the ws269 white mask tile 0_1 from paint269k.json minus the ws269 arrow fragment stroke
   (−379.34,−20.54)→(−378.65,−21.33) plus the turn arrow (0.30 m stem, 1.2 m head); new yellow-hatch tile x −340…−332,
   y −30…−23 (12 cm outline, 15 cm stripes every 0.9 m). 3 cm/px, anti-aliased. Tiles stay on the box (packed into the .blend);
   data/ws274_mask_tiles.json lists them.
4. `f274b.py` (on ws274a) → ws274b (saved 8:37:39 AM ET, promoted 8:37:47 AM ET, sha256 4bc81013…849e), then with f274a v3 (curb run
   extended from x −337 to −332, past the hatch to the red-roof building corner; self-review of the ws274b eye-from-E WIP) → ws274c =
   ws274c (saved 8:41:14 AM ET, promoted 8:41:15 AM ET, sha256 de547189…59f2; 105 curb rows, 1 raycast miss at the E end filled from
   the previous row), then with f274a v4 (reveal tapers to 2 cm over the last 1.2 m at both ends; the ws274c eye-from-E WIP showed
   a free-standing curb end at x −332) → ws274d = MAIN (saved 8:44:39 AM ET, promoted 8:44:41 AM ET, sha256 9432970e…eeee). f274b rebuilds the
   curb/gutter with f274a v2 (no clamp → one straight smoothed run; curb drops to a 2 cm lip over x −358.6…−354.4 where the police
   S walk meets the road, 0.8 m transitions = curb cut, UNVERIFIED), curb material WS27_curb_concrete_UNVERIFIED (the College Ave
   curbs) and a gutter copy of it (WS274_gutter_pan_concrete_WS27tone, 0.82× darker, roughness 0.85); the ws269 island curb gets the
   same curb material; the painted asphalt gets the new white tile and a yellow-hatch mask mixed after ws269_paint (colour
   (0.50,0.40,0.09), coverage 0.85, roughness 0.6).
5. Renders: `cams274.sh` (subrend234, terrain GN on, KEEPMOD, crop259), `jobwip274.sh` for the four WIPs on main.
6. Not done: Panzer N-wall drip strip — skipped as a guess (no photo of Panzer's N side; the ortho there is the gym eave and its
   shadow); the walk at the curb cut is still 2–13 cm below the curb lip (probe270b numbers), not re-probed.

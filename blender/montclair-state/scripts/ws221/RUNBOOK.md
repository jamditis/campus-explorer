# ws221 runbook (main ws220c -> ws221a -> ws221b -> ws221c)
Merges use scripts/ws208/merge208.py via run221.sh (CHAIN env, OUTN output; INF = input file), from the then-current main.
- ws221a: python3 mkmask221.py (copies the ws219 mask tiles to ws219{a,b,z}_mask_tile_N.png and writes 5-field tile lists
  data/ws219{a,b,z}_mask_tiles.json for tools/web-export/paint.py; the 8-field fix219b list is kept as ws219ab_mask_tiles_8field.json),
  CHAIN="ws221/fix221a.py"  (renames the 6 packed ws219 mask images to the exporter's (ws\d+[a-z]?)_mask_tile_ naming; filepaths untouched)
- ws221b: INF=montclair_state_ws221a.blend CHAIN="ws221/fix221b.py"  (W40: WS72 Kasser landing S outline over the WS70 verge straightened
  onto the chord from where it leaves the WS69 curb back to its corner on the W39 curb-return back; exposed verge grass raised)
- ws221c: INF=montclair_state_ws221b.blend CHAIN="ws221/fix221c.py"  (W41: WS67 gap asphalt E edge moved onto the diagonal WS27 W edge
  (wedge gap S of the curb junction); verge grass edge subdivided x4 and set 1 cm behind the curb-return back arc; road-side
  leftover verge grass dropped under the asphalt)
For a from-scratch rebuild, fix221a + fix221b + fix221c in that order reproduce ws221c.
Probes: runp.sh opens a file with every modifier off; dump221*.py / probe221*.py print P221 lines. Tests: t1.sh; WIPs: jobwip221.sh.

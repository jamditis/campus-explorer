# ws224 runbook (Nov 18, 2026 ~11:32 PM-12:10 AM ET): Kasser landing corner notch (W45b), curb joint, crossing seam, Kasser S verge (W46)
Main before: ws223h. Main after: ws224k (ws224j 11:52 PM + fix224k tree limb-up 11:56 PM; ws224b 11:39 PM, ws224c 11:40 PM, ws224d 11:43 PM, ws224h 11:48 PM, ws224j 11:52 PM ET).
All runs: INF=<file> OUTN=<out> CHAIN="..." bash scripts/ws224/run224.sh (merge208, modifiers off during the edit).
- ws224b = ws223h + fix224a (W45b ROOT CAUSE: the ws223d ring fan and the ws223f chord fill both covered the area SE of the
  WS220 curb-back arc = two stacked landing sheets over the curb top and up to ~10 cm past the curb front, hanging ~21 cm over
  the gutter; one simple polygon v130-v140-v150-v260..v266-v152-v142-v132 re-filled; no vertex moved)
  + fix224b (curb back rings k17-k26 RAISED 0.4-3.0 cm to slab edge - 3 mm; raise-only).
- ws224c = + fix224c (WS220 ring k29 shifted 1.6 cm horizontally onto WS27 curb_left ring 0, k28 half: flush curb face joint).
- ws224d = + fix224d (WS215 street-level walk verts under the WS72 W edge RAISED to slab - 2 mm; WS72 SW corner v0/v1 moved
  north 18 cm onto the WS215 S edge line, z kept) + fix224e (WS27 carriageway + WS67 gap asphalt: every face pointed DOWN;
  flipped up, no modifiers on either).
- ws224j = ws224d + fix224g (WS72 E edge raised to the WS71 W edge, 0.8-6.8 cm, tapered 1.5 m) + fix224h (walk-edge jog at
  x -243: WS72/WS71 edge verts moved horizontally onto the 0.30 m-from-curb line) + fix224j (WS71 raised under/before WS72b,
  up to 5.7 cm, tapered 3 m) + fix224f (NEW object WS224_Kasser_S_verge_grass_fill_UNVERIFIED: 0.3 m lawn verge strip between
  the walk edge and the curb_left back, x -247.5..-214.5, replacing a 25-35 cm bare-terrain trench). bbox205.json regenerated.
Rebuild from scratch: from ws223h CHAIN="ws224/fix224a.py ws224/fix224b.py ws224/fix224c.py ws224/fix224d.py ws224/fix224e.py
  ws224/fix224g.py ws224/fix224h.py ws224/fix224j.py ws224/fix224f.py".
Probes: probe224a/k (camera-ray object/face map, PCAM + PX), probe224c (stacked WS72 top faces), probe224e (evaluated stack
map), probe224j (objects whose faces mostly point down), others are one-off. WIPs: jobwip224.sh.
- ws224k = ws224j + fix224k (T_SugarMaple_L1_0281 low limb: single-user mesh copy, verts > 1 m from the trunk axis under
  ground + 2.4 m removed; tree is not sunk, the limb runs up the courtyard bank). Rebuild chain ends "... ws224/fix224f.py ws224/fix224k.py".

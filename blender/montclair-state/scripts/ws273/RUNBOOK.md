# ws273 runbook (Sat Nov 28, 2026, ~6:34 → ~7:25 AM ET) — UNIFY #4a/#4b: one lawn over the Sprague grandstand lawn and lot pocket

Main before: ws272c (sha a25f7823…). Backup montclair_state_pre_20261128ws273.blend = ws272c.
Last main session before the 7 AM ET building-day boundary: the Sprague grandstand lawn area (#4) is closed here.

1. Probes (merge208 loader, no save; `run273.sh`):
   - `probe273a.py` / `probe273b.py`: base-mesh materials around the lawn. The grandstand lawn E of x −249 is Terrain with
     WS82_Lawn_grandstand_no_ortho_UNVERIFIED; W of it WS68_RHD_ground_northDTM uses WS68_Ground_ortho_grass_north2020 (the
     straight tone line, #4a). The base Terrain has a hole at x −249…−236, y −112…−101 (old lot pocket).
   - `probe273c.py` / `probe273d.py` / `probe273e.py` (evaluated, per-mesh BVH): the PB_terrain_fan_regrid GN fills that hole with
     ~13,300 small faces carrying Ground_ortho_grass, which drapes the 2020 ortho there.
   - NJ 2020 0.1 m ortho (WMS, `url273.txt`; image not committed): the whole lawn block x ≈ −272…−236, y ≈ −96…−128 is a dark
     ribbed roof of a structure standing on the lot in 2020 (with its NE shadow), so every ortho-draped face there shows roof, not
     ground. What stands there now is UNVERIFIED (no post-2020 ortho on the NJ WMS; no photo).
   - `probe273f.py`: the regrid faces keep a correct 'ortho' UV (linear fit max error 0.013), so the material swap is safe.
2. `f273a.py` (on ws272c) → ws273a: (#4b) new last GN on Terrain that sets the WS82 lawn on Ground_ortho_grass faces with centres
   in x −249.2…−235.5, y −113.3…−105.5; (#4a) 888 WS68 faces with centres in x −273…−249, y −136…−98 → WS82 lawn (slot added
   to WS68). `f273b.py` → ws273b = MAIN (saved 6:45:01 AM ET, promoted 6:51:21 AM ET, sha256 7cc6dd74…33e1): renamed the GN
   WS273_lot_pocket_S_terrain_lawn_material so subset renders keep it (subrend234's terrain regex), viewport + render on.
3. Render finding: crop259 (render-only crop, first in the stack) runs before PB_terrain_fan_regrid, so subset renders leave the
   lot pocket empty and show a flat dark underlay slab with a black slot — the "dark rectangle" of ws271/ws272 obliques was
   mostly this artifact. Renders of this area use `CH=ws239/upd239.py` (no crop): peak 8.35 GB, GATE 9000.
   `jobwip273.sh`: before (ws272c backup) close-up + oblique, then the four WIPs on main.
4. Not done: the pocket's N tip (x −249…−237, y −105.5…−101.5, a triangle under the lot's diagonal S edge) keeps the ortho
   material (hidden by the lot edge in the WIPs); the new lawn edge at x −273 is a straight material edge to WS68's ortho lawn.

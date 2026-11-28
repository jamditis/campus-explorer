# ws272 runbook (Sat Nov 28, 2026, ~4:30 → ~5:15 AM ET) — UNIFY #4c WS68 S-edge ridge at the Panzer gym N wall

Main before: ws271c (sha e4364f10…). Backup montclair_state_pre_20261128ws272.blend = ws271c.

1. `probe272a.py` / `probe272b.py` (merge208 loader, no save): WS68_RHD_ground_northDTM base grid around its S edge (y −135) and
   the WS60 apron / WS86 target S of it. W of x −250 WS68 is DTM fill (no returns). Its last rows (x −278…−250, y −127…−135)
   climb south to 122.8 m, then drop 2–4 m to the apron (118.2–118.7 m) within 0.5 m; a 0.5–0.8 m pit sits at x −256…−253,
   y −130…−132. The measured Terrain E of x −249 falls south smoothly (122.4 → 119.0 m over y −126.5…−135.5), and WS68 W of
   x −279 falls south too. `probe272d.py`: the Panzer gym N wall is at y ≈ −136.8 (walls from z 117.0), so the "ridge" was
   ground piled against the gym wall above a dark slot.
2. `f272a.py` (on ws271c) → ws272a = MAIN (saved 4:34:41 AM ET, promoted 4:48:38 AM ET, sha256 04a1922c…): harmonic (Laplace)
   fill of the fill-only cells; boundaries: row y −126 (kept), columns x −279 and −248.6 (kept; E neighbour weighted for its 1.4 m
   spacing), S row y −135 snapped onto the apron top at the same x. 258 verts changed, max lower 4.08 m, max raise 0.34 m.
   `probe272c.py`: with WS68's own modifiers on, evaluated z is within 0.11 m of the base in the band (the GN modifiers don't
   re-snap here); the step at the S edge to the apron is ≤ 0.24 m (mean 0.02 m). Lawn only; no paving, walks or trees in the band.
   UNVERIFIED: the shape (no returns, no photo of Panzer's N side).
3. `f272b.py` (tried, not promoted): extended WS68 over the 1.5–1.9 m apron strip at the wall. Worse — the 2020 ortho there is
   the gym roof eave (pale streaks), and the dark band along the wall is the building's own shadow. Dropped.
4. Renders: `cams272.sh` (subrend234, terrain GN on, KEEPMOD, crop259; peak 6.4 GB, gate 7000). Before/after close-up:
   renders/test/20261128-0441_…ws271c_before… vs 20261128-0442_…ws272a…; oblique 20261128-0437 (before) vs 0439 (after).

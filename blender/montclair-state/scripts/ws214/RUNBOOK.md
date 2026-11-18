# ws214 RUNBOOK — main = ws214c (aaf6c8e6…), promoted 1:51:57 PM ET Nov 18
## DONE: W36 (fix214a.py S tip, fix214d.py N tip, fix214e.py lane-mouth lip + under-fill clamp) — merged.
## QUEUED: W35 Red Hawk Deck College Ave entrance — research done, rebuild not started
- Entry level: deck LEVEL 2 (et_rhd_lower_wearing_surface z 124.98, S edge y = −39.61 − 0.242·(x+278)); eu_rhd_ground_slab 121.5 is the lower level.
  Joe's Sep 2021 Street View: entrance at street/sidewalk level → consistent. KX_drive_apron TOP is already a plane road edge → 124.97 (do NOT regrade to 121.5;
  fix214b.py (full-column flatten) is WRONG — it collapses the apron skirt; not used).
- Real faults (test/20261118-1339_ws214_test_W35_E3_before.jpg): (1) KY_rhd_drive_side_walk_fill (E side, x −266…−264) warped pale strip below the apron edge;
  (2) LH_college_ave_gutter_asphalt_fill pieces lie as dark plates on the WS68 lawn S of the walk (x −268…−258, y −52…−50; parts at z 122.4, 2.4 m under the road);
  (3) E of the walk (x −265…−256, y −50…−44) is WS68 lawn; Street View shows street-level sidewalk with a red brick band to the SE core doors.
- Plan: build one sidewalk slab E of the apron (road curb back → deck face, top = KY edge + 0.15 m curb, flush with the apron at the drive edge via a curb drop),
  brick band per the photo (UNVERIFIED width), delete/sink the LH plates under it, clamp WS68 under it (Q6 evaluated check). W side bank: check in a W eye view.
- fix214c.py (grid sliver fill between KX and the walk) REJECTED — adds a jagged line (test …1340_ws214_test_W35_E3_after_c.jpg).
## Cameras (srun213 CAM strings)
- W36: C1 "-259.0,-53.5,126.6,-255.5,-58.5,124.9,30" C2 "-258.5,-60.5,126.3,-255.0,-56.5,125.0,35" C3 "-253.0,-63.5,126.2,-254.5,-58.5,125.0,32" CULL "-275,-235,-75,-40"
- W35: E1 "-270.5,-60.0,126.4,-270.5,-42.0,125.0,30" E2 "-254.0,-63.0,131.5,-270.0,-45.0,124.5,30" E3 "-262.0,-53.0,126.0,-267.0,-45.5,124.6,35" CULL "-300,-235,-80,-20"

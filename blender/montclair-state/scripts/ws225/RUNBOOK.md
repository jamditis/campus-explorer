# ws225 runbook (Nov 19, 2026 12:26-~12:55 AM ET): W47 down-facing ground sheets, W52 tree limb clearance probe, W53 east terrain diagnosis
Main before: ws224k. Main after: ws225a (promoted 12:42:54 AM ET).
- ws225a = ws224k + fix225b (W47 cont.: 19 ground-surface sheets whose faces ALL pointed down flipped up; only objects with no
  modifiers, single-user meshes, unmirrored transforms, names matching paving/landscape words; planters, riser fillers, curbs,
  ceilings/soffits/roofs/canopies excluded). Run: INF=montclair_state.blend OUTN=montclair_state_ws225a.blend CHAIN="ws225/fix225b.py" bash scripts/ws225/run225.sh
  (DRY=1 in the environment lists without flipping).
- probe225a: scene-wide tree limb clearance (802 deciduous tree objects) against RAW terrain + 196 paving meshes. Raw terrain is
  not trustworthy in the east (see probe225e), so use its paving-clearance column only.
- probe225c/d: tree trunk bases vs EVALUATED Terrain_LiDAR_DTM_1m (render-enabled modifiers only; d is the corrected run).
- probe225e: per-modifier terrain heights at 7 east points vs data/dtm_1m.npy (index [int(y+250), int(x+250)]).
- jobwip225.sh: the four WIPs. runp.sh: probe runner (modifiers off at load).

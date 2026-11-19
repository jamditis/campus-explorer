# ws233 runbook (Nov 19, 2026 8:33-~9:25 AM ET): W53o Stone Hall lower-storey windows at the lawn (north campus seam, item after W53b)
Main before: ws232b (045ddbd5...). Main after: ws233b (c5a918b2..., promoted 8:45:37 AM ET). Backup montclair_state_pre_20261119ws233.blend = ws232b.
FINDING (probe233a/b, EVALUATED ground): around TI_Stone_Hall_313028565_lower the ground is 135.97..136.97 (136.66 along the ESE
walk wall; USGS 3DEP agrees within 0.1-0.3 m). The procedural window shader (TR_Stone_brick_detail, rows at ti_z0+0.95+k*ti_floor,
1.47 m tall) used ti_z0 = 135.888, so the only ground-floor row ran 136.84..138.31 with the geometry sills (TR_Stone_window_sills) at
136.78..136.86: sills 0.1-0.2 m over the lawn, ground floor ~0.8 m below grade -> "windows meet the lawn" in the NE eye view.
EVIDENCE: Stone Hall = two residence floors (The Montclarion, 2016); Montclair State digitized slides 285/288 (1966) show the
ground-floor punched 2x2 windows on a cream brick base with sills ~1 m+ over the lawn (previews in refs/stone, not in the repo).
DECISION: ground-floor datum 136.9 (just above the highest adjacent grade 136.97; exact slab level UNVERIFIED).
- fix233a (interim, NOT promoted): a per-object window-minimum gate at 137.0 - wrong reading (sliced the window bottoms); superseded.
- fix233b (ws232b -> ws233b): lower-volume ti_z0 135.888 -> 136.9 (row 137.85..139.32, under the 140.11 fascia; the next row 141.05
  stays gated by z1-0.9), 592 sill verts +1.012 m (now 137.79..137.87), upper0 unchanged. 3 floating QS_Richardson grass points
  (104.9, 247.2, z 138.97 = 1.58 m over 3DEP) deleted.
- Specks (probe233d, scene ray casts from the WIP camera): the "2 dark specks above the walk" are far roof vents / exhaust-fan hoods
  (~156 m away, z ~146) of a building that the subset render does not append (the merged Roof_vent object's bbox overlaps the cull
  box). Subset-render artefact, not a model defect - no change.
- fix233c (tested, discarded): Granite_Curb (W-R7b). The base colour is MULTIPLY(granite image, 0.8): image mean 0.69 sRGB ~ 0.44
  linear, x 0.8 ~ 0.35 linear = already inside the grey-granite range (0.25-0.35). The near-white curb was the viewer reading the 0.8
  factor without the texture. .blend left unchanged.
Build: INF=<ws232b> OUTN=montclair_state_ws233b.blend CHAIN="ws233/fix233b.py" bash scripts/ws233/run233.sh
jobwip233.sh: four views (subrend226, terrain GN on, KEEPMOD paving drapes on). jobtest233.sh = the NE eye before/after test.

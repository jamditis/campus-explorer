# ws184 review cams = ws183 cams + one on the S drive from Lot 36 (exec tail183 with extra cam via env CAMSET)
src=open('/workspace/nj-scenes/montclair-state/scripts/ws183/tail183.py').read()
src=src.replace("('closeup_Lot36_SE_corner_toe_top',(-318.0,-230.5),9.0,(-318.0,-230.45),0.0,24)]",
 "('closeup_Lot36_SE_corner_toe_top',(-318.0,-230.5),9.0,(-318.0,-230.45),0.0,24),\n ('closeup_Lot3_S_drive_ramp_from_Lot36_SE',(-318.0,-241.0),2.2,(-308.0,-238.0),0.0,30),\n ('oblique_Lot3_S_drive_ramp_from_SW_high',(-326.0,-252.0),9.0,(-309.0,-238.0),0.0,26)]")
assert 'Lot3_S_drive_ramp' in src
exec(compile(src,'tail184','exec'))

cd /workspace/nj-scenes/montclair-state
export DLR=$(( $(date +%s) + 1800 ))
F=montclair_state_pre_20261116ws194.blend TAG=ws193a LIST="WS190_CAM_closeup_Lot3_S_ramp_E_edge=closeup_Lot3_S_ramp_E_edge_BEFORE" bash scripts/ws194/rend194.sh
F=montclair_state.blend TAG=ws194b LIST="WS190_CAM_closeup_Lot3_S_ramp_E_edge=closeup_Lot3_S_ramp_E_edge_AFTER WS191_CAM_eye_Lot3_S_ramp_from_E_looking_W=eye_Lot3_S_ramp_from_E_looking_W" bash scripts/ws194/rend194.sh

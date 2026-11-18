cd /workspace/nj-scenes/montclair-state
while pgrep -f "q194b?.sh" >/dev/null; do sleep 3; done
export DLR=$(( $(date +%s) + 1200 ))
F=montclair_state_pre_20261116ws194.blend TAG=ws193a LIST="WS194_CAM_closeup_ramp_E_edge=closeup_Lot3_S_ramp_E_edge_BEFORE WS194_CAM_eye_ramp_from_S_looking_N=eye_Lot3_S_ramp_from_S_looking_N_BEFORE" bash scripts/ws194/rend194n.sh
F=montclair_state.blend TAG=ws194c LIST="WS194_CAM_closeup_ramp_E_edge=closeup_Lot3_S_ramp_E_edge_AFTER WS194_CAM_eye_ramp_from_S_looking_N=eye_Lot3_S_ramp_from_S_looking_N_AFTER" bash scripts/ws194/rend194n.sh

cd /workspace/nj-scenes/montclair-state
while pgrep -f q194.sh >/dev/null; do sleep 3; done
export DLR=$(( $(date +%s) + 1500 ))
F=montclair_state_pre_20261116ws194.blend TAG=ws193a LIST="WS192_CAM_eye_Lot3_S_strip_from_W_looking_E=eye_Lot3_S_strip_from_W_looking_E_BEFORE" bash scripts/ws194/rend194.sh
F=montclair_state.blend TAG=ws194b LIST="WS192_CAM_eye_Lot3_S_strip_from_W_looking_E=eye_Lot3_S_strip_from_W_looking_E_AFTER WS192_CAM_oblique_Lot3_S_end_from_SW_high=oblique_Lot3_S_end_Sprague_from_SW_high" bash scripts/ws194/rend194.sh

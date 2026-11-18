cd /workspace/nj-scenes/montclair-state
bash scripts/ws177/run178.sh > scripts/ws177/run178.out 2>&1
if grep -q SAVED scripts/ws177/run178.out && [ -f montclair_state_ws177a.blend ]; then
 DLR=$(date -d '04:30' +%s) F=montclair_state_ws177a.blend TAG=ws177a CULL=-230,-90,-330,-260 LIST="WS177_CAM_oblique_NormalAve_N_side_from_S_high WS177_CAM_eye_NormalAve_N_walk_from_W_looking_E WS177_CAM_eye_NormalAve_N_curb_from_road_E_looking_W WS177_CAM_closeup_NormalAve_N_curb_verge_walk" bash scripts/ws177/rend177.sh > scripts/ws177/rend178.out 2>&1
fi
echo CHAIN_END $(date +%T) >> scripts/ws177/run178.out

# ws178 background watcher: merge ws177+ws178 fixes into montclair_state_ws178a.blend when MemAvailable >= 8.5 GB (until 05:00 ET),
# then render the 5 check views (until 05:50). Holds/refreshes /workspace/nj-scenes/.lock; removes it at the end. Does NOT promote.
cd /workspace/nj-scenes/montclair-state
L=/workspace/nj-scenes/.lock
echo "ws178 watcher pid $$ $(date) (merge gate until 05:00, renders until 05:50)" > $L
bash scripts/ws178/run178.sh > scripts/ws178/run178.out 2>&1
if grep -q SAVED scripts/ws178/run178.out && [ -f montclair_state_ws178a.blend ]; then
 echo "ws178 watcher pid $$ rendering $(date)" > $L
 DLR=$(date -d '05:50' +%s) F=montclair_state_ws178a.blend TAG=ws178a CULL=-230,-90,-330,-260 LIST="WS177_CAM_oblique_NormalAve_N_side_from_S_high WS177_CAM_eye_NormalAve_N_walk_from_W_looking_E WS177_CAM_eye_NormalAve_N_curb_from_road_E_looking_W WS177_CAM_closeup_NormalAve_N_curb_verge_walk" bash scripts/ws178/rend178.sh > scripts/ws178/rend178.out 2>&1
 echo "ws178 watcher pid $$ rendering lot3 $(date)" > $L
 DLR=$(date -d '05:55' +%s) F=montclair_state_ws178a.blend TAG=ws178a CULL=-345,-270,-275,-205 LIST="WS178_CAM_closeup_Lot3_aisle_S_drive_lawn_edge" bash scripts/ws178/rend178.sh >> scripts/ws178/rend178.out 2>&1
 sha256sum montclair_state_ws178a.blend >> scripts/ws178/run178.out
fi
echo CHAIN_END $(date +%T) >> scripts/ws178/run178.out
rm -f $L

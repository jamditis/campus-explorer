source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED"
srun "-20,40,-60,0" "20.0,-45.0,137.6,6.0,-30.0,135.8,30" ws226_test_W54_CCOM_dock_apron_shoulder_from_SE_ws226d_sub montclair_state_ws226d.blend test
srun "-80,-10,10,90" "-44.0,26.0,139.7,-44.0,55.0,138.1,30" ws226_test_W55_CafeDiem_patio_from_S_subrend226 montclair_state_ws226d.blend test

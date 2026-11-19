# ws226 final WIPs (main ws226f: W53 east terrain upper sheet + fan slivers removed, seam backing, trees re-seated; W54 apron
# lawn shoulder; W55 subrend226 appends objects linked from north/sprague_cafe_src.blend), subset renders, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED WS226_east_patch_seam_backing_UNVERIFIED"
F=montclair_state.blend
srun "100,250,-60,250" "110.0,-40.0,160.0,185.0,95.0,104.0,28" ws226_oblique_east_slope_terrain_W53_from_SW_ws226f_main_sub $F wip
srun "100,250,0,160" "180.0,110.0,107.9,150.0,60.0,106.0,30" ws226_eye_east_slope_W53_from_NE_ws226f_main_sub $F wip
srun "-80,-10,10,90" "-44.0,26.0,139.7,-44.0,55.0,138.1,30" ws226_eye_CafeDiem_patio_from_S_subrend226_ws226f_main_sub $F wip
srun "-5,30,-50,-15" "16.5,-42.5,136.6,10.0,-36.0,135.4,32" ws226_closeup_CCOM_dock_apron_lawn_shoulder_ws226f_main_sub $F wip

# ws227 final WIPs (main ws227g: W53c SE corner re-grid to dtm_1m + W53d apex fan re-triangulation + trees re-seated), subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED"
F=montclair_state.blend
srun "90,250,-250,-30" "80.0,-270.0,150.0,200.0,-140.0,93.0,28" ws227_oblique_SE_corner_terrain_W53c_from_SW_ws227g_main_sub $F wip
srun "120,250,-220,-80" "150.0,-150.0,101.2,200.0,-150.0,95.5,30" ws227_eye_SE_slope_W53c_from_W_ws227g_main_sub $F wip
srun "120,250,-200,-30" "200.0,-70.0,97.3,205.0,-140.0,94.5,30" ws227_eye_SE_slope_W53c_from_N_ws227g_main_sub $F wip
srun "95,140,-150,-105" "112.0,-120.0,104.8,122.0,-132.0,102.6,32" ws227_closeup_SE_regrid_seam_W53c_ws227g_main_sub $F wip

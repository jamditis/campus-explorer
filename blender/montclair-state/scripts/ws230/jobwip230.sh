# ws230 four WIPs (W53j NE east-edge gap fill + strip/QI re-height to USGS 3DEP 1 m), subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED WS230_NE_east_gap_fill_3DEP_UNVERIFIED"
F=${F:-montclair_state_ws230b.blend}; TAGM=${TAGM:-ws230b}
srun "120,280,-40,270" "120.0,-30.0,165.0,240.0,140.0,98.0,28" ws230_oblique_NE_east_edge_W53j_from_SW_${TAGM}_main_sub $F wip
srun "150,280,0,270" "205.0,60.0,100.8,248.0,150.0,97.5,30" ws230_eye_NE_east_edge_W53j_from_SW_${TAGM}_main_sub $F wip
srun "150,280,0,270" "243.0,185.0,106.0,238.0,60.0,95.0,30" ws230_eye_NE_east_edge_W53j_from_N_${TAGM}_main_sub $F wip
srun "180,280,40,180" "234.0,92.0,99.2,247.0,114.0,96.0,30" ws230_closeup_gap_fill_seam_W53j_${TAGM}_main_sub $F wip

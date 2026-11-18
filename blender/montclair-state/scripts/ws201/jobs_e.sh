C="-252,-222,-90,-68"; CB="-243.95,-74.59,128.0,-239.38,-80.93,126.0,28"
run $C "$CB" cut_ws201_ISA3_hairline_CU_BEFORE_ws201a montclair_state.blend test
IMP=$PWD/scripts/ws201/fix201d.npz run $C "$CB" cut_ws201_ISA3_hairline_CU_AFTER_fix201d montclair_state.blend test ws201/imp201b.py

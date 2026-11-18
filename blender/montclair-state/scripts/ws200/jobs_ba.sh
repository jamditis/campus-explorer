W5="-330,-300,-245,-220"; W18="-266,-212,-112,-78"
CW5="-321.5,-237.0,117.6,-312.0,-231.8,116.3,26"
CW18="-214.0,-114.0,131.0,-243.0,-99.0,123.8,28"
run $W5 "$CW5" cut_ws200_W5_bank_toe_CU_BEFORE_ws199a montclair_state.blend test
run $W5 "$CW5" cut_ws200_W5_bank_toe_CU_AFTER_ws200a montclair_state_ws200a.blend test
run $W18 "$CW18" cut_ws200_W18_Sprague_lot_oblique_BEFORE_ws199a montclair_state.blend test
run $W18 "$CW18" cut_ws200_W18_Sprague_lot_oblique_AFTER_ws200a montclair_state_ws200a.blend test

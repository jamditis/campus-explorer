W18="-266,-212,-112,-78"
C1="-236.0,-124.0,142.0,-240.0,-98.0,123.8,26"
run $W18 "$C1" cut_ws200_W18_Sprague_lot_oblique_S_BEFORE_ws199a montclair_state.blend test
run $W18 "$C1" cut_ws200_W18_Sprague_lot_oblique_S_AFTER_ws200a montclair_state_ws200a.blend test
run $W18 "-262.0,-101.0,125.0,-226.0,-100.0,125.4,26" cut_ws200_W18_eye_S_lot_from_W_BEFORE_ws199a montclair_state.blend test
run $W18 "-262.0,-101.0,125.0,-226.0,-100.0,125.4,26" cut_ws200_W18_eye_S_lot_from_W_AFTER_ws200a montclair_state_ws200a.blend test

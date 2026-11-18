#!/bin/bash
# Revert ws12 (SW Cole bed walk bridge rebuilt: extended 3.5 m toward plaza, widened to old walk edge, feathered ends, OZ-style joints object WS12_bridge_slab_joints_GN_UNVERIFIED) -> ws11 state (49b0c423...2360)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws12.blend montclair_state.blend && sha256sum montclair_state.blend

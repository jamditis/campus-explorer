#!/bin/bash
# Revert ws13 (brick soldier edging along both sides of the SW Cole bed walk bridge) -> ws12 state (cb48dcd7...3cff)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws13.blend montclair_state.blend && sha256sum montclair_state.blend

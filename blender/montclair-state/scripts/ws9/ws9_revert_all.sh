#!/bin/bash
# Revert ws9 (brick soldier edging on the Cole walk east of the plaza toward Morehead) -> ws8 state (317feb44...2b17)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws9.blend montclair_state.blend && sha256sum montclair_state.blend

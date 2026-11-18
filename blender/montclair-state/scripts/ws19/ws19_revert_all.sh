#!/bin/bash
# Revert ws19 -> ws18 state (0785f902...62eb)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws19.blend montclair_state.blend && sha256sum montclair_state.blend

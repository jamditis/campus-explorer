#!/bin/bash
# Revert ws11 (walk faces under COLE_planting_beds_smooth_bu SW of the plaza trimmed) -> ws10 state (0e62bdb7...3150)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws11.blend montclair_state.blend && sha256sum montclair_state.blend

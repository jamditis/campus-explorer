#!/bin/bash
# Revert ws3 (Cole plaza merge + material swaps) -> perf-opt 20261109 main (4d225131...6b05)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws3.blend montclair_state.blend && sha256sum montclair_state.blend

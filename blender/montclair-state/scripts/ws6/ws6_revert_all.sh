#!/bin/bash
# Revert ws6 (Cole entrance gable: glass wall -> white stucco + one tall arched window) -> ws5 state (18975dfb...bcd1)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws6.blend montclair_state.blend && sha256sum montclair_state.blend

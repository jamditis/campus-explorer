#!/bin/bash
# Revert ws7 (Cole gable base course + ws4 sign-bed shrubs) -> ws6 state (8189320c...2d5f)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws7.blend montclair_state.blend && sha256sum montclair_state.blend

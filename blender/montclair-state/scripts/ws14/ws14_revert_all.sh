#!/bin/bash
# Revert ws14 -> ws13 state (fb98e9d4...cd2e)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws14.blend montclair_state.blend && sha256sum montclair_state.blend

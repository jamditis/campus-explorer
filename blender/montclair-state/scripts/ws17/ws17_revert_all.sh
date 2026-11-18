#!/bin/bash
# Revert ws17 -> ws16 state (aa428371...c582)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws17.blend montclair_state.blend && sha256sum montclair_state.blend

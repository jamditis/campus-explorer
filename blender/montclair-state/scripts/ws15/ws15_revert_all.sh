#!/bin/bash
# Revert ws15 -> ws14 state (48770ee1...9967)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws15.blend montclair_state.blend && sha256sum montclair_state.blend

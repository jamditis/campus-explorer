#!/bin/bash
# Revert ws16 -> ws15 state (97926b67...c49a)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws16.blend montclair_state.blend && sha256sum montclair_state.blend

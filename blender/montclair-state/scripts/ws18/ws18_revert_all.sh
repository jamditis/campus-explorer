#!/bin/bash
# Revert ws18 -> ws17 state (f3679785...b6f8)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws18.blend montclair_state.blend && sha256sum montclair_state.blend

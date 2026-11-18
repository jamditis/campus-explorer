#!/bin/bash
# revert wl -> wk (35b50bf2...dbf0)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wl.blend montclair_state.blend && sha256sum montclair_state.blend

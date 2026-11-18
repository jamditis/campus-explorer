#!/bin/bash
# revert wn -> wm (de6ee28a...afe9d)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wn.blend montclair_state.blend && sha256sum montclair_state.blend

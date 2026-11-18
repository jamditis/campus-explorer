#!/bin/bash
# wa0 revert: REVERT_EXACT -> wz file (sha 9ee1dbec9f5d05207084aa2f657b78fba2a52d65d0006ef64a9c76bca34b1fa2)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wa0.blend montclair_state.blend
sha256sum montclair_state.blend

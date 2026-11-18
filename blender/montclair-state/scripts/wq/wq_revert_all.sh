#!/bin/bash
# wq revert: REVERT_EXACT restores the wp final (sha 344fb7a66d2a8d4daccf6152ed09da771f8535a88e09a736e2ea3feca7f07bfe)
# from the pre-wq backup.
set -e
cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wq.blend montclair_state.blend && sha256sum montclair_state.blend

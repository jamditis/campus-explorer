#!/bin/bash
# wa1 revert: REVERT_EXACT -> wa0 file (sha 3fe316e27ef5fbfa4b73f2683da3e91c584a77218459109d971ee487ba095e7a)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wa1.blend montclair_state.blend
sha256sum montclair_state.blend

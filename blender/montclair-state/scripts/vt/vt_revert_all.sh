#!/bin/bash
# vt REVERT: restore main to the vs final (pre-vt backup, sha 59f959cb...8c17fcb0)
set -e
cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261107vt.blend montclair_state.blend
sha256sum montclair_state.blend

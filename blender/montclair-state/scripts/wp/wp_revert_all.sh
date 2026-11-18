#!/bin/bash
# wp revert: REVERT_EXACT restores the wo final (sha d8ccc774…baae9) from the pre-wp backup.
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wp.blend montclair_state.blend && sha256sum montclair_state.blend

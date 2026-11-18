#!/bin/bash
# wr revert: REVERT_EXACT restores the wq final (sha af1098ada12d70099757327b7c87a6dbea6e285f4ca9b18ec65ba083dc5e38ff)
# from the pre-wr backup.
set -e
cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wr.blend montclair_state.blend && sha256sum montclair_state.blend

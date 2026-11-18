#!/bin/bash
# Nov 8 session wo (gully head) revert -> state before it (restored by Nov 9 wo after a name collision overwrote wo_revert_all.sh)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261108wo.blend montclair_state.blend && sha256sum montclair_state.blend

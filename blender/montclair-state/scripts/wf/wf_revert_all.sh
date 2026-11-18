#!/bin/sh
# revert wf -> we (5034b92e…83f3)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261108wf.blend montclair_state.blend && sha256sum montclair_state.blend

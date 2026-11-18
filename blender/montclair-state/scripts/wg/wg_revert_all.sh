#!/bin/sh
# revert wg -> wf (ceadc7e4…5479)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261108wg.blend montclair_state.blend && sha256sum montclair_state.blend

#!/bin/sh
# revert wh -> wg (ca17c32c…7119)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wh.blend montclair_state.blend && sha256sum montclair_state.blend

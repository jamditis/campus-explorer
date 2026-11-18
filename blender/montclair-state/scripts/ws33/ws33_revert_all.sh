#!/bin/bash
# ws33 revert: restore main from the pre-ws33 backup (= ws32 0629a66f…08e0)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws33.blend montclair_state.blend && sha256sum montclair_state.blend

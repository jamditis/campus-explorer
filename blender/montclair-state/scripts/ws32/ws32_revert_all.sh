#!/bin/bash
# ws32 revert: restore main from the pre-ws32 backup (= ws31 7e642a9e…a23a)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws32.blend montclair_state.blend && sha256sum montclair_state.blend

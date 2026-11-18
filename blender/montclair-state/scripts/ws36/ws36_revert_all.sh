#!/bin/bash
# ws36 revert: restore main from the pre-ws36 backup (= ws35 8e54aa42…3027)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws36.blend montclair_state.blend && sha256sum montclair_state.blend

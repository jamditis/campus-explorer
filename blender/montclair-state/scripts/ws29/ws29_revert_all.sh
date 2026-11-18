#!/bin/bash
# ws29 revert: restore main from the pre-ws29 backup (= ws28 7861a715…4417)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws29.blend montclair_state.blend && sha256sum montclair_state.blend

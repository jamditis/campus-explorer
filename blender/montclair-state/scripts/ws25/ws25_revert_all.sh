#!/bin/bash
# ws25 revert: restore main from the pre-ws25 backup (= ws24 3eed2abf…2577)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws25.blend montclair_state.blend && sha256sum montclair_state.blend

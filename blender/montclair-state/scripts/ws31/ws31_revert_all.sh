#!/bin/bash
# ws31 revert: restore main from the pre-ws31 backup (= ws30 452a35d6…1e21)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws31.blend montclair_state.blend && sha256sum montclair_state.blend

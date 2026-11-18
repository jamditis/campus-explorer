#!/bin/bash
# ws30 revert: restore main from the pre-ws30 backup (= ws29 53f08dd9…51c0)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws30.blend montclair_state.blend && sha256sum montclair_state.blend

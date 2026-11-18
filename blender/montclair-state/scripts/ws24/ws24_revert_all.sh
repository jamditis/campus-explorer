#!/bin/bash
# ws24 revert: restore main from the pre-ws24 backup (= ws23 126231b2…e3f)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws24.blend montclair_state.blend && sha256sum montclair_state.blend

#!/bin/bash
# ws37 revert: restore main from pre-ws37 backup (= ws36 43ff27db…c62e)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws37.blend montclair_state.blend && sha256sum montclair_state.blend

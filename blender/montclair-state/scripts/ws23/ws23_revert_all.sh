#!/bin/bash
# ws23 revert: restore main from the pre-ws23 backup (= ws22 7e67f325…cf3c)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws23.blend montclair_state.blend && sha256sum montclair_state.blend

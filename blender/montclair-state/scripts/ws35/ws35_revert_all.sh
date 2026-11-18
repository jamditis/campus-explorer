#!/bin/bash
# ws35 revert: restore main from the pre-ws35 backup (= ws34 69331ca0…3ef4)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws35.blend montclair_state.blend && sha256sum montclair_state.blend

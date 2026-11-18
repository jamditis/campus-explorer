#!/bin/bash
# ws26 revert: restore main from the pre-ws26 backup (= ws25 d475a59a…2a38)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws26.blend montclair_state.blend && sha256sum montclair_state.blend

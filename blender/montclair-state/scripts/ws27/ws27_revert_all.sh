#!/bin/bash
# ws27 revert: restore main from the pre-ws27 backup (= ws26 de7a616a…db88)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws27.blend montclair_state.blend && sha256sum montclair_state.blend

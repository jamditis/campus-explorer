#!/bin/bash
# ws28 revert: restore main from the pre-ws28 backup (= ws27 d8d6f8b5…3d57)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws28.blend montclair_state.blend && sha256sum montclair_state.blend

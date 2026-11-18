#!/bin/bash
# ws34 revert: restore main from the pre-ws34 backup (= ws33 346c79f8…0db9)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261110ws34.blend montclair_state.blend && sha256sum montclair_state.blend

#!/bin/bash
# revert ws122 window fix: restore main from pre-ws122 backup (sha b58da010...)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261113ws122.blend montclair_state.blend && sha256sum montclair_state.blend

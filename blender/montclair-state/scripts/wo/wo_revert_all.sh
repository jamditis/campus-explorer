#!/bin/bash
# revert wo -> wn (d06e2e47...d0ba7)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wo.blend montclair_state.blend && sha256sum montclair_state.blend

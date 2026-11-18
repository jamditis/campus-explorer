#!/bin/bash
# revert wk -> wj (841cc431...cdf94)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wk.blend montclair_state.blend && sha256sum montclair_state.blend

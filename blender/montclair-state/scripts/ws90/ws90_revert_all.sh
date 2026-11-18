#!/bin/bash
# revert main to before ws90 (= ws89 e0d97f32…)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261112ws90.blend montclair_state.blend && sha256sum montclair_state.blend

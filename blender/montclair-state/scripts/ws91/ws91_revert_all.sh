#!/bin/bash
# revert main to before ws91 (= ws90 7898fe68…)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261112ws91.blend montclair_state.blend && sha256sum montclair_state.blend

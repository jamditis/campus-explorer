#!/bin/bash
# restore MAIN to pre-ws75 (= ws74 b16ce875)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws75_reverted_from.blend && cp montclair_state_pre_20261111ws75.blend montclair_state.blend && echo reverted

#!/bin/bash
# restore MAIN to pre-ws82 (= ws81 a0235d54)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws82_reverted_from.blend && cp montclair_state_pre_20261112ws82.blend montclair_state.blend && echo reverted

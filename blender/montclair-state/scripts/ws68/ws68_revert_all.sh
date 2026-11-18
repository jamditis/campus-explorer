#!/bin/bash
# restore MAIN to the pre-ws68 state (= ws67b)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws68_reverted_from.blend && cp montclair_state_pre_20261111ws68.blend montclair_state.blend && echo reverted

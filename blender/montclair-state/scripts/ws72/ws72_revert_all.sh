#!/bin/bash
# restore MAIN to pre-ws72 (= ws71 67477cba)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws72_reverted_from.blend && cp montclair_state_pre_20261111ws72.blend montclair_state.blend && echo reverted

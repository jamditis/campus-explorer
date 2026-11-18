#!/bin/bash
# restore MAIN to pre-ws71 (= ws70b)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws71_reverted_from.blend && cp montclair_state_pre_20261111ws71.blend montclair_state.blend && echo reverted

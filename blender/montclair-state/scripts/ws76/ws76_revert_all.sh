#!/bin/bash
# restore MAIN to pre-ws76 (= ws75 329afbbe)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws76_reverted_from.blend && cp montclair_state_pre_20261111ws76.blend montclair_state.blend && echo reverted

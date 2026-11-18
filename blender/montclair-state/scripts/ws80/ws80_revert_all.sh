#!/bin/bash
# restore MAIN to pre-ws80 (= ws79 775a2c2b)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws80_reverted_from.blend && cp montclair_state_pre_20261112ws80.blend montclair_state.blend && echo reverted

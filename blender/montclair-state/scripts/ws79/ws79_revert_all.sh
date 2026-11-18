#!/bin/bash
# restore MAIN to pre-ws79 (= ws78 87a34fd2)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws79_reverted_from.blend && cp montclair_state_pre_20261112ws79.blend montclair_state.blend && echo reverted

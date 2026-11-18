#!/bin/bash
# restore MAIN to pre-ws81 (= ws80 ce59a0bc)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws81_reverted_from.blend && cp montclair_state_pre_20261112ws81.blend montclair_state.blend && echo reverted

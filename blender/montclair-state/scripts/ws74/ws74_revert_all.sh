#!/bin/bash
# restore MAIN to pre-ws74 (= ws73 2dbf532c)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws74_reverted_from.blend && cp montclair_state_pre_20261111ws74.blend montclair_state.blend && echo reverted

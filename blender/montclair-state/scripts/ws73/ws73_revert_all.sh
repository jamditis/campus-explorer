#!/bin/bash
# restore MAIN to pre-ws73 (= ws72 4e5f629f)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws73_reverted_from.blend && cp montclair_state_pre_20261111ws73.blend montclair_state.blend && echo reverted

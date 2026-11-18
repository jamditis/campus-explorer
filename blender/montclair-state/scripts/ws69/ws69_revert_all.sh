#!/bin/bash
# restore MAIN to the pre-ws69 state (= ws68c)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws69_reverted_from.blend && cp montclair_state_pre_20261111ws69.blend montclair_state.blend && echo reverted

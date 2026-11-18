#!/bin/bash
# wa2 revert -> wa1 (sha a793f76b016ac6e6f6befa282e1087473fd9daa27856f916fe96abf47d6d0759)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wa2.blend montclair_state.blend
sha256sum montclair_state.blend

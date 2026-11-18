#!/bin/bash
# wd revert -> wc (sha 73a1e50de038359f514a8fbcfa74e68a539edecc3e3de4b8260b53fdac2f9c4f)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wd.blend montclair_state.blend
sha256sum montclair_state.blend

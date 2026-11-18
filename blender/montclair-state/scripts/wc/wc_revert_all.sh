#!/bin/bash
# wc revert -> wb (sha 700c416d4f90dbe3b2c639528a8b8ad58436e3e92aee3057e78e20590b10e0ee)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wc.blend montclair_state.blend
sha256sum montclair_state.blend

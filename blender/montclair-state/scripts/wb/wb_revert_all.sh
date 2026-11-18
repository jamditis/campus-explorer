#!/bin/bash
# wb revert -> wa2 (sha 6176ac73ba79a74b87de64cea6668662269bab764005b1f45b6120d224c0d774)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wb.blend montclair_state.blend
sha256sum montclair_state.blend

#!/bin/bash
# we revert -> wd (sha cbfb1f5a21aa9e061a1fc140f8873e2997a7b0075eb1838f2941472fff5d9f1d)
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108we.blend montclair_state.blend
sha256sum montclair_state.blend

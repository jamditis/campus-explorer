#!/bin/bash
# revert wm -> wl (dbcce17e...52f6a4)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wm.blend montclair_state.blend && sha256sum montclair_state.blend

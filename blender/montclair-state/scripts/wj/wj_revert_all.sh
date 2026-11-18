#!/bin/bash
# revert wj -> wi2 (22050fad...f94fd2)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wj.blend montclair_state.blend && sha256sum montclair_state.blend

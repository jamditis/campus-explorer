#!/bin/bash
# revert wi2 -> wh (21acd927...ca87b)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wi2.blend montclair_state.blend && sha256sum montclair_state.blend

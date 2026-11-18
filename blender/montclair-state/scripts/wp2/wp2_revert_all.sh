#!/bin/bash
# revert wp2 -> wo (main 8aab6acc...8c2a; north 093c80c3...)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109wp2.blend montclair_state.blend && cp north/montclair_north_pre_20261109wp2.blend north/montclair_north.blend && sha256sum montclair_state.blend north/montclair_north.blend

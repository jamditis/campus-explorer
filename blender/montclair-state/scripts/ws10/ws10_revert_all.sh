#!/bin/bash
# Revert ws10 (brick edging on the Footpaths_OSM walk from the Cole sign bed toward Morehead + limbed-up pin oaks 0274/0277 over that walk) -> ws9 state (04bbb8b4...6f14)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws10.blend montclair_state.blend && sha256sum montclair_state.blend

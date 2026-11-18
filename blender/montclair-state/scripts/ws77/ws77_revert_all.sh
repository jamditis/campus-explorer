#!/bin/bash
# restore MAIN to pre-ws77 (= ws76 5986306a)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws77_reverted_from.blend && cp montclair_state_pre_20261111ws77.blend montclair_state.blend && echo reverted

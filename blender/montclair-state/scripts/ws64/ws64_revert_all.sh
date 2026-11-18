#!/bin/bash
# revert ws64 Kasser-north band-to-DTM (restores the pre-ws64 backup)
cd /workspace/nj-scenes/montclair-state && [ -f montclair_state_pre_20261111ws64.blend ] && cp montclair_state_pre_20261111ws64.blend montclair_state.blend && echo reverted

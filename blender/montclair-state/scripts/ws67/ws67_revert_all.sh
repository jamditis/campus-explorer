#!/bin/bash
# revert ws67 College Ave west regrade (restores the pre-ws67 backup)
cd /workspace/nj-scenes/montclair-state && [ -f montclair_state_pre_20261111ws67.blend ] && cp montclair_state_pre_20261111ws67.blend montclair_state.blend && echo reverted

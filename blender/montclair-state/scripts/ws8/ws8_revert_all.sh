#!/bin/bash
# Revert ws8 (plaza pavers retoned to sunlit grey + walk tip under the W mulch bed removed) -> ws7 state (0f9c467a...4eba)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws8.blend montclair_state.blend && sha256sum montclair_state.blend

#!/bin/bash
# Revert ws4 (corridor walk retone + Cole walk kit placement) -> ws3 main (d67152bc...c726)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws4.blend montclair_state.blend && sha256sum montclair_state.blend

#!/bin/bash
# Revert ws5 (Cole plaza circle + quatrefoil, entrance roof red tile, sign moved) -> ws4 state (59c19d36...25c3)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261109ws5.blend montclair_state.blend && sha256sum montclair_state.blend

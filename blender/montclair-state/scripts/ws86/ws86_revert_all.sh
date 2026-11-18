#!/bin/bash
# restore main to the pre-ws86 backup (ws83 sha 20798b3c...)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261112ws86.blend montclair_state.blend && sha256sum montclair_state.blend

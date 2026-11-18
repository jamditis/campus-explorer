#!/bin/bash
# restore MAIN to pre-ws78 (= ws77 31b24883)
cd /workspace/nj-scenes/montclair-state && cp montclair_state.blend montclair_state_ws78_reverted_from.blend && cp montclair_state_pre_20261112ws78.blend montclair_state.blend && echo reverted

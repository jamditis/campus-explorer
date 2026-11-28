#!/bin/bash
# ws273: the four WIPs on main ws273c, no render crop (see RUNBOOK step 3).
cd /workspace/nj-scenes/montclair-state
for c in 1 2 3 4; do F=montclair_state.blend TAGM=ws273c D=wip GATE=9000 CH=ws239/upd239.py ONLY=$c bash scripts/ws273/cams273.sh; done
echo JOBDONE

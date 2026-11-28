#!/bin/bash
# ws274: four WIPs on main ws274e (College Ave N curb/gutter, arrow, hatch), terrain on, crop259 (no PB-regrid area in view).
cd /workspace/nj-scenes/montclair-state
for c in 1 2 3 4; do F=montclair_state.blend TAGM=ws274e D=wip GATE=4300 ONLY=$c bash scripts/ws274/cams274.sh; done
echo JOBDONE

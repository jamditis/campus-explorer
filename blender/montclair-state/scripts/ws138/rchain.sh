cd /workspace/nj-scenes/montclair-state
D=${D:-wip}
for c in "$@"; do NEED=6000 MAXW=600 DIR=$D bash scripts/ws138/waitmem.sh bash scripts/ws138/rt.sh montclair_state.blend "$c"; done; echo ALLEND

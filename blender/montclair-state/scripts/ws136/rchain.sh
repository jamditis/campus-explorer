cd /workspace/nj-scenes/montclair-state
for c in "$@"; do NEED=6500 MAXW=900 DIR=wip bash scripts/ws136/waitmem.sh bash scripts/ws136/rt.sh montclair_state.blend "$c"; done; echo ALLEND

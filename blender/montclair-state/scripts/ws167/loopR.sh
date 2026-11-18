cd /workspace/nj-scenes/montclair-state
for c in "$@"; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 9000 ]; do sleep 10; done
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws167c bash scripts/ws166/rt.sh montclair_state_ws167c.blend $c
done; echo "$(date +%T) ALL DONE"

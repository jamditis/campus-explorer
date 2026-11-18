cd /workspace/nj-scenes/montclair-state
for t in 1 2 3 4 5 6; do bash scripts/ws161/go161.sh && break; echo "$(date +%T) retry $t"; sleep 15; done

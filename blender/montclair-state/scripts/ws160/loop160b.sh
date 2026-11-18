cd /workspace/nj-scenes/montclair-state
for t in 1 2 3 4 5 6; do bash scripts/ws160/go160b.sh && break; echo "$(date +%T) retry $t"; sleep 15; done

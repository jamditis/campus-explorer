cd /workspace/nj-scenes/montclair-state
D=/workspace/nj-scenes/exports/model-20261125; F=$D/montclair_state_20261125.blend; SRC=/workspace/nj-scenes/montclair-state/montclair_state.blend
echo "$(sha256sum $SRC)"
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4000 ] && ! pgrep -x blender >/dev/null; do sleep 3; done
echo "$(date +%T) strip (merge208 low-mem)"
CHAIN=ws244/strip244_lowmem.py INF=$SRC OUT=$F WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws208/merge208.py > scripts/ws244/strip244.out 2>&1
ls -la $F || exit 2
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 3000 ]; do sleep 3; done
F=$F WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws244/ver244_lowmem.py 2>&1 | grep -E "VER|WATCH" > scripts/ws244/ver244.out
cat scripts/ws244/ver244.out
grep -q "libs \[\]" scripts/ws244/ver244.out || { echo VERFAIL; exit 3; }
SZ=$(stat -c %s $F); [ $SZ -lt 2000000000 ] || { echo TOOBIG; exit 4; }
(cd $D && sha256sum montclair_state_20261125.blend > SHA256SUMS.txt && cat SHA256SUMS.txt)
echo "STRIPDONE $(date +%T)"

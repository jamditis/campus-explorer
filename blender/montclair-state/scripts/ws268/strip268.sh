cd /workspace/nj-scenes/montclair-state
D=/workspace/nj-scenes/exports/model-20261127; F=$D/montclair_state_20261127.blend; SRC=/workspace/nj-scenes/montclair-state/montclair_state.blend
mkdir -p $D
echo "$(sha256sum $SRC)"
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-4000} ] && ! pgrep -x blender >/dev/null; do sleep 3; done
echo "$(date +%T) strip (merge208 low-mem)"
rm -f $F  # never verify/checksum a stale file from an earlier run
CHAIN=ws244/strip244_lowmem.py INF=$SRC OUT=$F WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws208/merge208.py > scripts/ws268/strip268.out 2>&1
RC=$?
[ $RC -eq 0 ] && grep -q "^SAVED" scripts/ws268/strip268.out && ! grep -q "WATCHDOG KILL" scripts/ws268/strip268.out || { echo "STRIPFAIL rc=$RC"; exit 2; }
ls -la $F || exit 2
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 3000 ]; do sleep 3; done
F=$F WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws244/ver244_lowmem.py 2>&1 | grep -E "VER|WATCH" > scripts/ws268/ver268.out
cat scripts/ws268/ver268.out
grep -q "libs \[\]" scripts/ws268/ver268.out && grep -qx "VER unpacked \[\]" scripts/ws268/ver268.out || { echo VERFAIL; exit 3; }
SZ=$(stat -c %s $F); [ $SZ -lt 2000000000 ] || { echo TOOBIG; exit 4; }
(cd $D && sha256sum montclair_state_20261127.blend > SHA256SUMS.txt && cat SHA256SUMS.txt)
echo "STRIPDONE $(date +%T)"

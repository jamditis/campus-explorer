cd /workspace/nj-scenes/montclair-state
D=/workspace/nj-scenes/exports/model-20261118e; F=$D/montclair_state_20261118e.blend
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4500 ] && ! pgrep -x blender >/dev/null; do sleep 3; done
echo "$(date +%T) strip"
OUT=$F WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --factory-startup --python scripts/ws215/strip215.py > scripts/ws217/strip217.out 2>&1
ls -la $F || exit 2
/workspace/opt/blender/blender -b $F --factory-startup --python scripts/ws215/ver215.py 2>&1 | grep VER > scripts/ws217/ver217.out
cat scripts/ws217/ver217.out
grep -q "libs \[\]" scripts/ws217/ver217.out || { echo VERFAIL; exit 3; }
SZ=$(stat -c %s $F); [ $SZ -lt 2000000000 ] || { echo TOOBIG; exit 4; }
(cd $D && sha256sum montclair_state_20261118e.blend > SHA256SUMS.txt && cat SHA256SUMS.txt)
gh release create model-20261118e -R jamditis/campus-explorer --title "Model 2026-11-18e (ws217)" --notes-file $D/NOTES.md $F $D/SHA256SUMS.txt
echo "EXIT $? $(date +%T)"

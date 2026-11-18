cd /workspace/nj-scenes/montclair-state
echo "$(date +%T) start avail $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
FIXES="ws182/fix182.py ws183/fix183.py ws184/fix184.py ws185/fix185.py ws186/fix186.py" TAIL=ws186/tail186.py TAG=ws186_subset SAMP=24 WD_MIN=1500 timeout 1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws182/sub182.py 2>&1 | grep -E "WROTE|FIX186|rror|Trace|WATCH"
echo "$(date +%T) done"

#!/bin/bash
# run blender with RSS + avail watch; kill if avail < 500 MB
"$@" & PID=$!; peak=0; minav=999999
while kill -0 $PID 2>/dev/null; do r=$(ps -C blender -o rss= | sort -n | tail -1); a=$(free -m | awk '/^Mem:/{print $7}')
 [ -n "$r" ] && [ "$r" -gt "$peak" ] && peak=$r; [ "$a" -lt "$minav" ] && minav=$a
 if [ "$a" -lt 350 ]; then echo KILL_LOWMEM; pkill -P $PID; kill $PID; pkill -f 'blender -b'; fi; sleep 2; done
echo peak_kb $peak minavail_mb $minav

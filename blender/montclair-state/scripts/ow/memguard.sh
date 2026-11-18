#!/bin/bash
# kill any blender process if MemAvailable < 600 MB for 2 consecutive checks; log every 2 s
LOG=/workspace/nj-scenes/montclair-state/data/ow/memwatch.log; low=0
while true; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); r=$(ps -C blender -o rss= | awk '{s+=$1}END{print int(s/1024)}')
 echo "$(date +%H:%M:%S) avail=$a blender_rss=$r" >> $LOG
 if [ "$a" -lt 600 ]; then low=$((low+1)); else low=0; fi
 if [ $low -ge 2 ]; then echo "$(date +%H:%M:%S) KILL blender (avail $a)" >> $LOG; pkill -9 -x blender; low=0; fi
 sleep 2; done

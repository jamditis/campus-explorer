#!/bin/bash
# watchdog + RSS trace (kills if MemAvailable < WD_MIN)
"$@" & P=$!; t0=$(date +%s.%N); mx=0
while kill -0 $P 2>/dev/null; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 B=$(pgrep -P $P -f blender | head -1); [ -z "$B" ] && B=$P
 r=$(awk '/VmRSS/{print int($2/1024)}' /proc/$B/status 2>/dev/null); r=${r:-0}; [ $r -gt $mx ] && mx=$r
 echo "T $(echo "$(date +%s.%N)-$t0"|bc|cut -c1-5) rss=$r avail=$a" >> ${TRACE:-/tmp/trace150.txt}
 if [ "$a" -lt ${WD_MIN:-700} ]; then echo "WATCHDOG KILL avail=$a rss=$r"; pkill -9 -P $P; kill -9 $P; fi; sleep 0.25; done
wait $P; echo "MAXRSS $mx"

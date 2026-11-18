#!/bin/bash
cd /workspace/nj-scenes/montclair-state
gate(){ while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" \> "${GIVEUP:-0000}" ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt ${GATE:-7000} ] && break; sleep 3; done; echo "$(date +%T) $1 START $a"; }
gate MAIN
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws110/main110b.py 2>&1 | grep -E "E110|INV110|MOD110|G110|P110|M110|CUT|rror|Trace|WATCH"
sha256sum montclair_state.blend | cut -c1-16; echo "$(date +%T) DONE"; echo END

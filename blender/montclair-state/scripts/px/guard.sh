#!/bin/bash
# run a command, kill blender if available memory < 350 MB; report min avail
"$@" & P=$!; MIN=99999; while kill -0 $P 2>/dev/null; do A=$(free -m | awk '/Mem:/{print $7}'); [ $A -lt $MIN ] && MIN=$A; if [ $A -lt 350 ]; then pkill -f "nj-scenes|montclair_state|pw_test_copy" -n; pkill -f "blender -b" ; echo KILLED_LOWMEM; fi; sleep 1; done; echo MIN_AVAIL $MIN

# wait until MemAvailable > ${NEED:-9000} MB (max ${MAXW:-600}s), then run "$@"
t=0; while [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -lt ${NEED:-9000} ] && [ $t -lt ${MAXW:-600} ]; do sleep 3; t=$((t+3)); done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; "$@"

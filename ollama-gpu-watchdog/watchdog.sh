#!/bin/bash
# Keep Ollama's loaded models fully in GPU memory.
#
#     watchdog.sh check [HOST]            # print each loaded model and how much of it is on the GPU
#     watchdog.sh watch [HOST] [SECONDS]  # every SECONDS (default 60): if a model is partly on the CPU,
#                                         # unload every model; the next request reloads only what it needs
#
# HOST defaults to http://localhost:11434. Stop `watch` with Ctrl-C or kill. It only calls Ollama's
# API (/api/ps, and /api/generate with keep_alive 0); it changes no configuration.
set -u
mode=${1:-check}
host=${2:-http://localhost:11434}
every=${3:-60}

loaded() {  # name, bytes in GPU memory, total bytes, one model per line
  curl -s --max-time 5 "$host/api/ps" | python3 -c '
import json, sys
for m in json.load(sys.stdin)["models"]:
    print(m["name"], m["size_vram"], m["size"])'
}

case $mode in
  check)
    loaded | awk '{printf "%-28s %5.2f of %5.2f GB on the GPU (%3.0f%%)%s\n", $1, $2/1e9, $3/1e9, 100*$2/$3, ($2<$3 ? "   <- partly on the CPU" : "")}'
    ;;
  watch)
    while sleep "$every"; do
      spill=$(loaded | awk '$2 < $3 {print $1}' | paste -sd ' ')
      [ -z "$spill" ] && continue
      for m in $(loaded | awk '{print $1}'); do
        # keep_alive 0: unload when idle. A request in flight finishes first.
        curl -s --max-time 900 "$host/api/generate" -d "{\"model\":\"$m\",\"keep_alive\":0}" > /dev/null
      done
      echo "$(date +%T) $spill was partly on the CPU; unloaded every model"
    done
    ;;
  *) echo "usage: $0 check|watch [HOST] [SECONDS]" >&2; exit 2 ;;
esac

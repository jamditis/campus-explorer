# ws267: run the ws264 pre-release check inside merge208's low-memory loader (all modifiers off at load_post, nothing
# evaluated, NO SAVE). Plain `blender -b main.blend --python m5check264.py` evaluates the full scene at load and was
# watchdog-killed at 1.39 GB even when started with 7.3 GB available. The check only reads datablocks/paths/base meshes.
import os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws264/m5check264.py').read())
print('M5C264 END',flush=True)
os._exit(0)

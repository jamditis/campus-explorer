# ws248f rebuild from ws248b: f248c (patch, walk, wider joints) -> f248d (shrunk delete box) -> k248e (full-cover drops) -> f248e
cd /workspace/nj-scenes/montclair-state
INF=$PWD/montclair_state_ws248b.blend GATE=2800 CHAIN=ws248/f248c.py OUTN=montclair_state_ws248f1.blend bash scripts/ws248/run248c.sh
INF=$PWD/montclair_state_ws248f1.blend GATE=2800 CHAIN=ws248/f248d.py OUTN=montclair_state_ws248f2.blend bash scripts/ws248/run248d.sh
F=montclair_state_ws248f2.blend timeout 600 /workspace/opt/blender/blender -b --factory-startup --python scripts/ws248/k248e.py 2>&1 | grep -E "K248E|rror"
INF=$PWD/montclair_state_ws248f2.blend GATE=2800 CHAIN=ws248/f248e.py OUTN=montclair_state_ws248f.blend bash scripts/ws248/run248e.sh
F=montclair_state_ws248f.blend timeout 600 /workspace/opt/blender/blender -b --factory-startup --python scripts/ws248/k248.py 2>&1 | grep -E "K248|rror" | cut -c1-400

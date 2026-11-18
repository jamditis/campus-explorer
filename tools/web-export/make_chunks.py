# Step 2: assign renderable objects to export chunks (tiles) -> chunks.json
import collections
import json
import math
import os
import re

WORK = os.environ.get("WORK", "/workspace/nj-scenes/web/build/main")
d = json.load(open(WORK + "/objects.json"))
EXCL = re.compile(
    r"(grass_points|grass_fill|Lawn_grass|_grass_|cx_grass|GN instances|people placeholders|task chairs|Context_ground_beyond|_CAM_|^CAM_|WALK_\d|RETIRED|_bak_|walk_joints_auto|slab_joints_GN|panel_tone_chips)",
    re.I,
)
TILE = 160.0
ch = collections.defaultdict(list)
skipped = []
for n, v in d.items():
    if not v["v"]:
        continue
    if EXCL.search(n):
        skipped.append(n)
        continue
    if v["t"] == "EMPTY" and not v["inst"]:
        continue
    x0, x1, y0, y1 = v["bb"][:4]
    w = max(x1 - x0, y1 - y0)
    if n.startswith("Context_skirt"):
        key = "skirt"  # real-elevation 4 km far-field terrain, exported with its skirt_under GN
    elif w > 350 or n.startswith(("BD_", "MID_")):
        key = "context"
    else:
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        key = "t_%d_%d" % (math.floor(cx / TILE), math.floor(cy / TILE))
    ch[key].append(n)
tri = lambda k: sum(d[n]["tri"] for n in ch[k])
out = {k: dict(objects=sorted(ch[k]), tri=tri(k)) for k in sorted(ch)}
json.dump(out, open(WORK + "/chunks.json", "w"), indent=0)
for k in out:
    print(k, len(out[k]["objects"]), out[k]["tri"])
print("skipped", len(skipped))

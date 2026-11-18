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
PREFIX = os.environ.get("PREFIX", "")
# Unified campus: a secondary scene (north) merged into the main world. Same Blender origin, so no
# transform; main wins everywhere it already has geometry. Objects whose names exist in main are
# skipped (the main copies are the maintained ones), objects centred in a cell main covers are skipped,
# and the secondary terrain is clipped to cells main doesn't cover (clip.json, applied by export_web).
MERGE = os.environ.get("MERGE_WITH", "")
CELL = 10.0
occ = set()
mainnames = set()
if MERGE:
    md = json.load(open(MERGE + "/objects.json"))
    mch = json.load(open(MERGE + "/chunks.json"))
    exported = {o for k, v in mch.items() if k != "skirt" for o in v["objects"]}
    mainnames = set(md)
    GROUND = re.compile(r"terrain|DTM|ground|apron|lawn|paving|asphalt|walk|curb|grass", re.I)
    TREE = re.compile(r"^(NT|NTx|T|Tree|MID)_|tree|shrub", re.I)

    def cells(x0, x1, y0, y1):
        for i in range(math.floor(x0 / CELL), math.floor(x1 / CELL) + 1):
            for j in range(math.floor(y0 / CELL), math.floor(y1 / CELL) + 1):
                yield (i, j)

    bld = set()
    for n in exported:
        v = md[n]
        x0, x1, y0, y1 = v["bb"][:4]
        w = max(x1 - x0, y1 - y0)
        if n.startswith(("BD_", "MID_")) or w > 700:
            continue
        if GROUND.search(n):
            occ.update(cells(x0, x1, y0, y1))  # main ground: its whole footprint
        elif v["t"] == "MESH" and v["tri"] > 50 and w < 150 and not TREE.search(n):
            bld.update(cells(x0, x1, y0, y1))  # main buildings and site features
    json.dump(dict(cell=CELL, cells=sorted(occ)), open(WORK + "/clip.json", "w"))
    print("merge: main ground covers", len(occ), "cells, main buildings", len(bld), "cells of", CELL, "m")
CLIPPED = re.compile(r"terrain|apron", re.I)
DROP = re.compile(r"skirt|Context_", re.I)
ch = collections.defaultdict(list)
skipped = []
merged_out = collections.Counter()
# buildings are kept or dropped whole: group by name prefix, drop a group only if most of it overlaps main
grp = lambda n: re.split(r"[ _]", n)[0]
gover = collections.Counter()
gall = collections.Counter()
if MERGE:
    for n, v in d.items():
        x0, x1, y0, y1 = v["bb"][:4]
        c = (math.floor((x0 + x1) / 2 / CELL), math.floor((y0 + y1) / 2 / CELL))
        gall[grp(n)] += 1
        gover[grp(n)] += c in bld
for n, v in d.items():
    if not v["v"]:
        continue
    if EXCL.search(n):
        skipped.append(n)
        continue
    if MERGE:
        x0, x1, y0, y1 = v["bb"][:4]
        c = (math.floor((x0 + x1) / 2 / CELL), math.floor((y0 + y1) / 2 / CELL))
        if n in mainnames:
            merged_out["same name in main"] += 1
            continue
        if DROP.search(n):
            merged_out["far-field (main has its own)"] += 1
            continue
        if CLIPPED.search(n):
            pass  # terrain: exported, faces in main ground cells removed by export_web
        elif (GROUND.search(n) or TREE.search(n)) and c in occ:
            merged_out["ground/tree on main ground"] += 1
            continue
        elif gover[grp(n)] > 0.5 * gall[grp(n)]:
            merged_out["overlaps a main building"] += 1
            continue
    if v["t"] == "EMPTY" and not v["inst"]:
        continue
    x0, x1, y0, y1 = v["bb"][:4]
    w = max(x1 - x0, y1 - y0)
    if MERGE:
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        w = max(x1 - x0, y1 - y0)
        key = PREFIX + ("context" if w > 350 else "t_%d_%d" % (math.floor(cx / TILE), math.floor(cy / TILE)))
    elif n.startswith("Context_skirt"):
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
print("skipped", len(skipped), dict(merged_out))

# writes models/main/manifest.json (one unified campus) (tile list with centres for nearest-first loading, sizes,
# paint layers, snapshot time ET).  env: OUT, SCENE, FILE, SOURCE_VERSION, SOURCE_SAVED, TILE
import datetime
import glob
import json
import os
import re

S = os.environ.get("OUT", "/workspace/nj-scenes/web/campus/models/main")
src = os.environ.get("FILE", "/workspace/nj-scenes/montclair-state/montclair_state.blend")
TILE = float(os.environ.get("TILE", "160"))
tiles = []
for f in sorted(glob.glob(S + "/*.glb")):
    t = dict(file=os.path.basename(f), bytes=os.path.getsize(f))
    m = re.match(r"(?:n_)?t_(-?\d+)_(-?\d+)\.glb$", t["file"])
    if m:
        # Blender XY tile centre -> three.js XZ (z = -y)
        t["center"] = [(int(m[1]) + 0.5) * TILE, -(int(m[2]) + 0.5) * TILE]
    tiles.append(t)
order = {"skirt.glb": 0, "context.glb": 1, "n_context.glb": 1, "far_houses.glb": 1}
tiles.sort(key=lambda t: (order.get(t["file"], 2), t["file"]))
mt = datetime.datetime.fromtimestamp(os.path.getmtime(src))
ver = os.environ.get("SOURCE_VERSION", "")
saved = os.environ.get("SOURCE_SAVED") or mt.strftime("%B %-d, %Y, %-I:%M %p ET")
scene = os.environ.get("SCENE", "main")
paint = json.load(open(S + "/paint.json")) if os.path.exists(S + "/paint.json") else []
old = json.load(open(S + "/manifest.json")) if os.path.exists(S + "/manifest.json") else {}
# one unified campus built from several source .blends: keep each one's snapshot label
sources = old.get("sources") or {}
if not sources and old.get("source_saved"):
    sources["main"] = dict(saved=old["source_saved"], version=old.get("source_version", ""))
sources[scene] = dict(saved=saved, version=ver, file=os.path.basename(src))
head = sources.get("main", sources[scene])
json.dump(
    dict(
        tiles=tiles,
        paint=paint,
        source_saved=head["saved"],
        source_version=head["version"],
        sources=sources,
        # far-field land cover and trees from tools/web-export/landcover.py (OpenStreetMap + 3DEP DEM)
        landcover=dict(file="landcover.webp", half=2000) if os.path.exists(S + "/landcover.webp") else None,
        far_trees="far_trees.bin" if os.path.exists(S + "/far_trees.bin") else None,
        exported=datetime.datetime.now().strftime("%B %-d, %Y, %-I:%M %p ET"),
        total_bytes=sum(t["bytes"] for t in tiles),
    ),
    open(S + "/manifest.json", "w"),
    indent=1,
)
print("manifest", len(tiles), sum(t["bytes"] for t in tiles))

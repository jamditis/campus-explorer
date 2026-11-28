# writes models/main/manifest.json (one unified campus) (tile list with centres for nearest-first loading, sizes,
# paint layers, snapshot time ET).  env: OUT, SCENE, FILE, SOURCE_VERSION, SOURCE_SAVED, TILE
import datetime
import glob
import json
import os
import re

from glb_refs import shared_bytes, uri_files

S = os.environ.get("OUT", "/workspace/nj-scenes/web/campus/models/main")
src = os.environ.get("FILE", "/workspace/nj-scenes/montclair-state/montclair_state.blend")
TILE = float(os.environ.get("TILE", "160"))
tiles = []
for f in sorted(glob.glob(S + "/*.glb")):
    t = dict(file=os.path.basename(f), bytes=os.path.getsize(f))
    m = re.match(r"(?:n_|sw_)?t_(-?\d+)_(-?\d+)\.glb$", t["file"])
    if m:
        # Blender XY tile centre -> three.js XZ (z = -y)
        t["center"] = [(int(m[1]) + 0.5) * TILE, -(int(m[2]) + 0.5) * TILE]
        lod = S + "/lod/" + t["file"]
        if os.path.exists(lod):
            t["lod"] = "lod/" + t["file"]  # far-distance version (lod.mjs)
            t["lod_bytes"] = os.path.getsize(lod)
            if lod_tex := uri_files(S, t["lod"]):
                t["lod_tex"] = lod_tex
    # shared files the tile refers to (images in tex/, share_tex.mjs; geometry packs in geo/, share_geo.mjs):
    # downloaded once, whichever tile asks first
    if tex := uri_files(S, t["file"]):
        t["tex"] = tex
    tiles.append(t)
# every file a tile or far version names, with its size (a missing one stops the export here)
named = {f for t in tiles for f in t.get("tex", []) + t.get("lod_tex", [])}
tex_sizes = {f: os.path.getsize(os.path.join(S, f)) for f in sorted(named)}
order = {"skirt.glb": 0, "context.glb": 1, "n_context.glb": 1, "sw_context.glb": 1, "far_houses.glb": 1}
tiles.sort(key=lambda t: (order.get(t["file"], 2), t["file"]))
scene = os.environ.get("SCENE", "main")
# SOURCE_VERSION_<SCENE> / SOURCE_SAVED_<SCENE> label one source; plain SOURCE_VERSION / SOURCE_SAVED label
# main only, so a value exported for the main run cannot relabel the north model
def label(key):
    v = os.environ.get(f"{key}_{scene.upper()}")
    return v if v is not None else (os.environ.get(key, "") if scene == "main" else "")
ver = label("SOURCE_VERSION")
paint = json.load(open(S + "/paint.json")) if os.path.exists(S + "/paint.json") else []
old = json.load(open(S + "/manifest.json")) if os.path.exists(S + "/manifest.json") else {}
# one unified campus built from several source .blends: keep each one's snapshot label
sources = old.get("sources") or {}
if not sources and old.get("source_saved"):
    sources["main"] = dict(saved=old["source_saved"], version=old.get("source_version", ""))
# KEEP_SOURCES=1 (site.sh): the site build has no .blend, so the labels stay as the export left them
if os.environ.get("KEEP_SOURCES") != "1" or scene not in sources:
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(src)) if os.path.exists(src) else None
    saved = label("SOURCE_SAVED") or (mt.strftime("%B %-d, %Y, %-I:%M %p ET") if mt else "")
    sources[scene] = dict(saved=saved, version=ver, file=os.path.basename(src))
head = sources.get("main", sources[scene])
# main ground meshes the north merge superseded (make_chunks writes them into the north work dir's clip.json)
WN = os.environ.get("WORK_NORTH", "/workspace/nj-scenes/web/build/north")
clip = json.load(open(WN + "/clip.json")) if os.path.exists(WN + "/clip.json") else {}
hide = clip.get("hide_main", old.get("hide", []))
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
        hide=hide,
        exported=datetime.datetime.now().strftime("%B %-d, %Y, %-I:%M %p ET"),
        # the tiles' own bytes and, once each, the shared files (images, geometry) they name (far versions are not counted)
        tex=tex_sizes,
        total_bytes=sum(t["bytes"] for t in tiles) + shared_bytes(tiles, tex_sizes),
    ),
    open(S + "/manifest.json", "w"),
    indent=1,
)
print("manifest", len(tiles), sum(t["bytes"] for t in tiles) + shared_bytes(tiles, tex_sizes))

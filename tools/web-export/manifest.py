# writes web/campus/models/main/manifest.json (tile list, sizes, snapshot time ET)
import datetime
import glob
import json
import os

S = "/workspace/nj-scenes/web/campus/models/main"
tiles = [
    dict(file=os.path.basename(f), bytes=os.path.getsize(f))
    for f in sorted(glob.glob(S + "/*.glb"))
]
tiles.sort(key=lambda t: (t["file"] != "context.glb", t["file"]))
src = "/workspace/nj-scenes/montclair-state/montclair_state.blend"
mt = datetime.datetime.fromtimestamp(os.path.getmtime(src))
ver = (
    open("/workspace/nj-scenes/web/SOURCE_VERSION").read().strip()
    if os.path.exists("/workspace/nj-scenes/web/SOURCE_VERSION")
    else ""
)
SS = "/workspace/nj-scenes/web/SOURCE_SAVED"
saved = open(SS).read().strip() if os.path.exists(SS) else mt.strftime("%B %-d, %Y, %-I:%M %p ET")
json.dump(
    dict(
        tiles=tiles,
        source_saved=saved,
        source_version=ver,
        exported=datetime.datetime.now().strftime("%B %-d, %Y, %-I:%M %p ET"),
        total_bytes=sum(t["bytes"] for t in tiles),
    ),
    open(S + "/manifest.json", "w"),
    indent=1,
)
print("manifest", len(tiles), sum(t["bytes"] for t in tiles))

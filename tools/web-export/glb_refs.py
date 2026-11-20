"""Files a published tile names by URI (the shared images in models/main/tex/, from share_tex.mjs).

Used by manifest.py (per-tile image lists and true download sizes) and tools/ci/check_viewer_refs.py.
"""

import json
import os
import posixpath
import struct


def gltf_json(path):
    """The JSON chunk of a GLB."""
    with open(path, "rb") as f:
        head = f.read(20)
        length, kind = struct.unpack("<II", head[12:20])
        if head[:4] != b"glTF" or kind != 0x4E4F534A:
            raise ValueError(f"{path}: not a GLB")
        return json.loads(f.read(length))


def image_files(base, tile):
    """Files the images of `tile` (a path relative to `base`) refer to, relative to `base`, in order."""
    out = []
    for im in gltf_json(os.path.join(base, tile)).get("images", []):
        uri = im.get("uri")
        if not uri or uri.startswith("data:"):
            continue
        path = posixpath.normpath(posixpath.join(posixpath.dirname(tile), uri))
        if path not in out:
            out.append(path)
    return out


def shared_bytes(tiles, sizes):
    """Bytes of the files that `tiles` (manifest entries with a `tex` list) refer to, each file once."""
    return sum(sizes[f] for f in {f for t in tiles for f in t.get("tex", [])})

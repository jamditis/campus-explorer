"""Shared tile images (tools/web-export/share_tex.mjs): what the manifest and the CI check read."""

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "web-export"))

import glb_refs  # noqa: E402


def write_glb(path, gltf):
    text = json.dumps(gltf).encode()
    text += b" " * (-len(text) % 4)
    body = struct.pack("<II", len(text), 0x4E4F534A) + text
    Path(path).write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


class GlbRefsTest(unittest.TestCase):
    def test_external_uris_relative_to_the_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "lod").mkdir()
            images = [
                {"uri": "../tex/a.webp"},
                {"bufferView": 0, "mimeType": "image/webp"},
                {"uri": "data:image/png;base64,AA"},
            ]
            write_glb(Path(d) / "lod" / "t_0_0.glb", {"images": images})
            write_glb(Path(d) / "t_0_0.glb", {"images": [{"uri": "tex/a.webp"}]})
            write_glb(Path(d) / "skirt.glb", {"asset": {}})
            self.assertEqual(glb_refs.image_files(d, "lod/t_0_0.glb"), ["tex/a.webp"])
            self.assertEqual(glb_refs.image_files(d, "t_0_0.glb"), ["tex/a.webp"])
            self.assertEqual(glb_refs.image_files(d, "skirt.glb"), [])

    def test_geometry_packs_are_files_the_tile_names(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "lod").mkdir()
            gltf = {
                "images": [{"uri": "../tex/a.webp"}],
                # the binary chunk and the meshopt fallback buffer have no URI; a pack does
                "buffers": [
                    {"byteLength": 8},
                    {"byteLength": 99},
                    {"uri": "../geo/p.bin", "byteLength": 4},
                ],
            }
            write_glb(Path(d) / "lod" / "t_0_0.glb", gltf)
            self.assertEqual(glb_refs.uri_files(d, "lod/t_0_0.glb"), ["tex/a.webp", "geo/p.bin"])
            self.assertEqual(glb_refs.image_files(d, "lod/t_0_0.glb"), ["tex/a.webp"])

    def test_shared_bytes_count_each_file_once(self):
        tiles = [{"tex": ["tex/a.webp", "tex/b.webp"]}, {"tex": ["tex/a.webp"]}, {}]
        sizes = {"tex/a.webp": 100, "tex/b.webp": 7, "tex/c.webp": 50}
        self.assertEqual(glb_refs.shared_bytes(tiles, sizes), 107)


if __name__ == "__main__":
    unittest.main()

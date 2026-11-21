"""Check that the viewer's local references resolve.

For every HTML file outside vendor/: src/href attributes and import-map targets
that point at local files must exist. Relative imports in the viewer's JavaScript
(static and dynamic) and files it fetches by a literal relative path must exist.
Every tile a model manifest lists must exist, including the campus manifest that
joins the scenes, and so must every file a listed tile names by URI (the shared
images in models/main/tex/ and geometry packs in models/main/geo/). External URLs are ignored.
"""

import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web-export"))
from glb_refs import uri_files  # noqa: E402

ATTR = re.compile(r"""(?:src|href)\s*=\s*["']([^"'#?]+)""", re.I)
IMPORTMAP = re.compile(r"<script[^>]*type=[\"']importmap[\"'][^>]*>(.*?)</script>", re.S | re.I)
JS_IMPORT = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(?\s*)["'](\.{1,2}/[^"']+)["']""")
JS_FETCH = re.compile(r"""\bfetch\(\s*["'](\.{1,2}/[^"'$]+)["']""")


def is_local(ref):
    return not re.match(r"^(?:[a-z]+:|//|#|data:|mailto:)", ref, re.I) and ref.strip() != ""


def missing_files(base, files):
    """Files that the GLBs `files` (relative to `base`) name by URI but that do not exist."""
    out = []
    for f in files:
        if not f or not f.endswith(".glb") or not os.path.exists(os.path.join(base, f)):
            continue
        for ref in uri_files(base, f):
            if not os.path.exists(os.path.join(base, ref)):
                out.append(f"{base}/{f}: names missing file {ref}")
    return out


def main():
    problems = []
    html = [
        p
        for p in subprocess.run(
            ["git", "ls-files", "*.html"], capture_output=True, text=True, check=True
        ).stdout.split()
        if not p.startswith("vendor/")
    ]
    for page in html:
        base = os.path.dirname(page)
        text = open(page, encoding="utf-8").read()
        refs = ATTR.findall(text)
        for block in IMPORTMAP.findall(text):
            refs += [v for v in json.loads(block).get("imports", {}).values()]
        for ref in refs:
            if not is_local(ref):
                continue
            target = os.path.normpath(
                os.path.join(base, ref.lstrip("/") if ref.startswith("/") else ref)
            )
            if ref.endswith("/"):
                ok = os.path.isdir(target)
            else:
                ok = os.path.exists(target)
            if not ok:
                problems.append(f"{page}: missing local reference {ref}")
    scripts = [
        p
        for p in subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.js"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        if not p.startswith(("vendor/", "tools/", "tests/"))
    ]
    for script in scripts:
        text = open(script, encoding="utf-8").read()
        for ref in JS_IMPORT.findall(text):
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(script), ref))):
                problems.append(f"{script}: imports missing file {ref}")
        # fetch() paths resolve against the page, which is served from the repository root
        for ref in JS_FETCH.findall(text):
            if not os.path.exists(os.path.normpath(ref)):
                problems.append(f"{script}: fetches missing file {ref}")
    for manifest in glob.glob("models/manifest.json") + glob.glob("models/*/manifest.json"):
        data = json.load(open(manifest))
        tiles = data.get("tiles", []) if isinstance(data, dict) else []
        for t in tiles:
            name = t.get("file") if isinstance(t, dict) else t
            if name and not os.path.exists(os.path.join(os.path.dirname(manifest), name)):
                problems.append(f"{manifest}: lists missing tile {name}")
            lod = t.get("lod") if isinstance(t, dict) else None
            if lod and not os.path.exists(os.path.join(os.path.dirname(manifest), lod)):
                problems.append(f"{manifest}: lists missing far version {lod}")
            problems += missing_files(os.path.dirname(manifest), [name, lod])
    for p in problems:
        print(f"::error::{p}")
    print(f"viewer refs: {len(html)} page(s), {len(scripts)} script(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

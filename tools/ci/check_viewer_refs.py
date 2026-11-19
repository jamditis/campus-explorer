"""Check that the viewer's local references resolve.

For every HTML file outside vendor/: src/href attributes and import-map targets
that point at local files must exist. If a model manifest exists, every tile it
lists must exist too. External URLs are ignored.
"""

import glob
import json
import os
import re
import subprocess
import sys

ATTR = re.compile(r"""(?:src|href)\s*=\s*["']([^"'#?]+)""", re.I)
IMPORTMAP = re.compile(r"<script[^>]*type=[\"']importmap[\"'][^>]*>(.*?)</script>", re.S | re.I)


def is_local(ref):
    return not re.match(r"^(?:[a-z]+:|//|#|data:|mailto:)", ref, re.I) and ref.strip() != ""


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
    for manifest in glob.glob("models/*/manifest.json"):
        data = json.load(open(manifest))
        tiles = data.get("tiles", []) if isinstance(data, dict) else []
        for t in tiles:
            name = t.get("file") if isinstance(t, dict) else t
            if name and not os.path.exists(os.path.join(os.path.dirname(manifest), name)):
                problems.append(f"{manifest}: lists missing tile {name}")
            lod = t.get("lod") if isinstance(t, dict) else None
            if lod and not os.path.exists(os.path.join(os.path.dirname(manifest), lod)):
                problems.append(f"{manifest}: lists missing far version {lod}")
    for p in problems:
        print(f"::error::{p}")
    print(f"viewer refs: {len(html)} page(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

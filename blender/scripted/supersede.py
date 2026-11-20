"""Write the rules for tools/web-export/supersede.mjs: for every area, the footprint outline and
which meshes of the other source models are ground inside it (<area>/footprint.json, "supersede").

usage: python3 blender/scripted/supersede.py OUT.json [--areas NAME,NAME]
Every area's rules are written, so marks of other areas stay known; `--areas` marks the rest `skip`.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import layout  # noqa: E402


def main():
    args = sys.argv[1:]
    out = []
    chosen = {d.name for d in layout.areas(args)}
    for plan_dir in layout.areas():
        if not (plan_dir / "footprint.json").exists():
            continue  # interiors only: the area owns no ground
        rules = json.loads(Path(plan_dir / "footprint.json").read_text())["supersede"]
        ring = [[round(x, 3), round(y, 3)] for x, y in layout.load(plan_dir)["footprint"]]
        out.append(
            dict(
                name=plan_dir.name,
                skip=plan_dir.name not in chosen,
                footprint=ring,
                clip=rules["clip"],
                drop=rules.get("drop", []),
                tuck=rules.get("tuck", 0.5),
            )
        )
        print(
            f"supersede rules {plan_dir.name}: {len(ring)} footprint points,",
            f"{len(rules['clip'])} clip and {len(rules.get('drop', []))} drop patterns",
        )
    json.dump(dict(areas=out), open(args[0], "w"))


if __name__ == "__main__":
    main()

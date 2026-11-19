"""Write the rules for tools/web-export/supersede.mjs: the footprint outline and which meshes of the
other
source models are ground inside it (plan/footprint.json, "supersede").

usage: python3 blender/southwest/supersede.py OUT.json [--plan DIR]
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import layout  # noqa: E402


def main():
    args = sys.argv[1:]
    plan_dir = Path(args[args.index("--plan") + 1]) if "--plan" in args else HERE / "plan"
    rules = json.loads(Path(plan_dir / "footprint.json").read_text())["supersede"]
    ring = [[round(x, 3), round(y, 3)] for x, y in layout.load(plan_dir)["footprint"]]
    json.dump(
        dict(
            footprint=ring,
            clip=rules["clip"],
            drop=rules.get("drop", []),
            tuck=rules.get("tuck", 0.5),
        ),
        open(args[0], "w"),
    )
    print(
        "supersede rules:",
        len(ring),
        "footprint points,",
        len(rules["clip"]),
        "clip and",
        len(rules.get("drop", [])),
        "drop patterns",
    )


if __name__ == "__main__":
    main()

"""Corrections to the main model's College of Communication and Media (CCOM) that its interior
survey against Joe's two evacuation floor plans (2026-11-20) found. Run on a copy of the main
.blend, headless, and save under a new name (AGENTS.md):

    blender -b MAIN.blend --python blender/ccom_main_fixes.py -- OUT.blend [--dry-run]

Only reversible changes: objects are hidden from render and viewport (`hide_render`,
`hide_viewport`), none is deleted. Each change says why. Larger corrections that need modelling
(the east band's roof, the atrium turned 13.7 degrees off the shell) are listed in ROADMAP-style
notes in `LATER` and are not done here.
"""

import re
import sys

# (pattern on the object name, reason). A pattern matches the whole name.
HIDE = [
    (
        r"Campus sign lettering(\.\d+)?",
        "reads 'SCHOOL OF COMMUNICATION AND MEDIA'; the building is the College of Communication "
        "and Media and the real sign's text is not known from any source (build_scene.py l.2119)",
    ),
    (
        r"dd_SOUTH0_back_(wall|base)",
        "the floor 1 sign has no wall here: it cuts rooms 1005 and 1005B",
    ),
    (
        r"NG (connector|link) (W wall|E wall|N wall|N end wall \(behind east facade\)|ceiling"
        r"|LED \d|light( \d)?)",
        "corridor square to the model axes that crosses rooms 1011, 1023 and 1020 of the sign",
    ),
]

LATER = [
    "The roof over the east band (a >= 20 in the building frame, b -21..13) is at 143.1: one "
    "storey. The LiDAR DSM has 147.5 to 150.7 there and the floor 2 sign has rooms 2025..2035: "
    "raise the roof (School of Communication and Media roof (LiDAR), hip + ridge cap tiles, "
    "CCOM_east_* roof plates) to the LiDAR, then drop the scripted area's east_low_roof keep-out.",
    "The atrium, hallway, S office, N classroom and their furnishing (NG, NH (inside), NJ, NK, "
    "NO, NP, NS, OC, OD, OE, OA, OB) are square to the model axes, 13.7 deg off the shell: turn "
    "them about the atrium centre or rebuild them from the sign; the stair then runs along the "
    "north wall at about a -12.7..-8.2 (sign), not a -17..-11.",
    "The newsroom back offices and mezzanine sit about 2.5 m west of the sign's 1002A..1002B3 "
    "and 2002..2012, as five equal rooms.",
    "The window units (CCOM_Win_Wing_A instances) carry 3 m deep fake-room boxes inside the "
    "building (z 138.7..144.9) that fill the perimeter rooms and block walking.",
    "The lobby video wall (about 5 x 2.5 m, Joe's photo 1000102886) and its light shelf on the "
    "wood panel wall are missing.",
]


def plan(names):
    """(name, reason) for every object name that a HIDE rule matches, in the order given."""
    rules = [(re.compile(p), why) for p, why in HIDE]
    out = []
    for n in names:
        for rx, why in rules:
            if rx.fullmatch(n):
                out.append((n, why))
                break
    return out


def main():
    import bpy

    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    dry = "--dry-run" in args
    todo = plan([o.name for o in bpy.data.objects])
    for name, why in todo:
        ob = bpy.data.objects[name]
        print(f"hide {name}: {why}")
        if not dry:
            ob.hide_render = True
            ob.hide_viewport = True
    print(f"{len(todo)} objects", "(dry run)" if dry else "hidden")
    for note in LATER:
        print("later:", note)
    out = [a for a in args if not a.startswith("--")]
    if out and not dry:
        bpy.ops.wm.save_as_mainfile(filepath=out[0], compress=True)
        print("saved", out[0])


if __name__ == "__main__":
    main()

"""Adopt hand-made objects of the main model into the scripted build (an area's `adopt.json`).

The listed objects are appended from a main-model release .blend with what they need (meshes,
materials and their packed images, node groups, modifier targets), moved by their group's
transform in world space and linked into the build, so the web export writes them into sw_ tiles.
They keep their modifiers, instancing and material names, so the export sees them as it sees them
in the main tiles: the same applied modifiers, the same material categories (`cat`), the same far
version rules. What changes: names start with `SW_adopt_` (cut to Blender's 63 bytes), parents are
cleared with the world transform kept, and a moved object whose modifiers read another object
(a boolean cutter, a geometry-nodes object input) is made a plain mesh first, so the other object
cannot pull it back.

The pure parts (names, the transform, the plan check, finding the file) need no Blender.
"""

import hashlib
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "web-export"))

from export_skip import EXCL  # noqa: E402

PREFIX = "SW_adopt_"
MAX_NAME = 63  # bytes: Blender cuts longer names
TRANSFORM_KEYS = {"rotate_z_deg", "about", "translate"}
GROUP_KEYS = {"name", "objects", "transform", "text", "why"}


def export_skips(name):
    """Does the web export leave an object of this name out of every tile? Then the main tiles
    never showed it, and it is not adopted."""
    return bool(EXCL.search(name))


def _cut(text, size):
    """`text` cut to at most `size` UTF-8 bytes, never inside a character."""
    return text.encode()[:size].decode(errors="ignore")


def adopt_name(name, taken):
    """The build's name for source object `name`: `SW_adopt_<name>`. One that is too long, or
    already taken, is cut and ends with a short hash of the whole source name (the same every
    run), and with `_UNVERIFIED` when the source name carried that label (or the start of it)."""
    full = PREFIX + name
    label = "UNVERI" in name.upper()
    whole = not label or "UNVERIFIED" in name.upper()  # Blender may have cut the label already
    if len(full.encode()) <= MAX_NAME and full not in taken and whole:
        return full
    for n in range(6, 41):
        tail = "~" + hashlib.sha1(name.encode()).hexdigest()[:n]
        if label:
            tail += "_UNVERIFIED"
        out = _cut(full, MAX_NAME - len(tail.encode())).rstrip(" _(") + tail
        if out not in taken:
            return out
    raise ValueError(f"no free name for {name!r}")


def group_matrix(transform):
    """4x4 matrix (rows) of a group's transform: turn `rotate_z_deg` anticlockwise about the
    vertical through `about` [x, y], then move by `translate` [x, y, z]. None: the identity."""
    t = transform or {}
    extra = set(t) - TRANSFORM_KEYS
    if extra:
        raise ValueError(f"unknown transform keys {sorted(extra)}; use {sorted(TRANSFORM_KEYS)}")
    a = math.radians(t.get("rotate_z_deg", 0.0))
    c, s = math.cos(a), math.sin(a)
    px, py = (list(t.get("about", [0.0, 0.0])) + [0.0, 0.0])[:2]
    tx, ty, tz = (list(t.get("translate", [0.0, 0.0, 0.0])) + [0.0, 0.0, 0.0])[:3]
    # p' = R (p - about) + about + translate
    return [
        [c, -s, 0.0, px - c * px + s * py + tx],
        [s, c, 0.0, py - s * px - c * py + ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def check(plan):
    """Check an `adopt` block. Returns [(object name, group)] in plan order."""
    f = plan.get("file", "")
    if not f or Path(f).name != f:
        raise ValueError(f"adopt file must be a base name, not {f!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", plan.get("sha256", "")):
        raise ValueError("adopt sha256 must be 64 lower-case hex digits")
    rows, seen = [], {}
    if not plan.get("groups"):
        raise ValueError("adopt needs at least one group")
    for g in plan["groups"]:
        extra = set(g) - GROUP_KEYS
        if extra:
            raise ValueError(f"group {g.get('name')!r}: unknown keys {sorted(extra)}")
        if not g.get("name") or not g.get("objects"):
            raise ValueError(f"group {g.get('name')!r} needs a name and objects")
        group_matrix(g.get("transform"))
        for n in g["objects"]:
            if n in seen:
                raise ValueError(f"{n!r} is in groups {seen[n]!r} and {g['name']!r}")
            seen[n] = g["name"]
            rows.append((n, g))
        for n, body in (g.get("text") or {}).items():
            if n not in g["objects"] or not isinstance(body, str):
                raise ValueError(f"group {g['name']!r}: text for {n!r}, not one of its objects")
    return rows


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def source(plan, adopt_from, assets):
    """The release file to adopt from: `adopt_from` (the file, or a folder holding plan["file"]),
    else plan["file"] in the folder of `assets`. Stops the build when it is missing or its sha256
    is not the plan's."""
    if adopt_from is not None:
        p = Path(adopt_from)
        path = p / plan["file"] if p.is_dir() else p
    elif assets is not None:
        path = Path(assets).parent / plan["file"]
    else:
        raise SystemExit(f"adopt: give --adopt-from PATH (or --assets) to find {plan['file']}")
    if not path.is_file():
        raise SystemExit(f"adopt: {path} not found")
    got = sha256(path)
    if got != plan["sha256"]:
        raise SystemExit(f"adopt: {path} has sha256 {got}, the plan asks for {plan['sha256']}")
    return path


# ---------- Blender ----------


def _reads_other_object(ob):
    """Does a modifier of `ob` read another object or a collection (boolean cutter, curve,
    geometry-nodes object input, Object Info node)? Then moving `ob` alone changes its shape."""
    import bpy

    def tree_reads(nt, depth=0):
        for n in nt.nodes:
            if n.bl_idname in ("GeometryNodeObjectInfo", "GeometryNodeCollectionInfo"):
                return True
            if n.type == "GROUP" and n.node_tree and depth < 8:
                if tree_reads(n.node_tree, depth + 1):
                    return True
        return False

    for m in ob.modifiers:
        if not m.show_render:
            continue
        for p in m.bl_rna.properties:
            if p.type == "POINTER" and p.identifier != "rna_type":
                v = getattr(m, p.identifier, None)
                if isinstance(v, bpy.types.Object | bpy.types.Collection) and v != ob:
                    return True
        if m.type == "NODES":
            if any(isinstance(m[k], bpy.types.Object | bpy.types.Collection) for k in m.keys()):
                return True
            if m.node_group and tree_reads(m.node_group):
                return True
    return False


def _bake(ob):
    """Make `ob` a plain mesh of what its modifiers give (instances realised), in its own frame."""
    import bpy

    vl = bpy.context.view_layer
    for o in vl.objects.selected:
        o.select_set(False)
    ob.select_set(True)
    vl.objects.active = ob
    with bpy.context.temp_override(active_object=ob, selected_objects=[ob], object=ob):
        bpy.ops.object.convert(target="MESH")
    ob.select_set(False)


def build(plan, path, coll):
    """Append, move and link the objects of one `adopt` block from release file `path` into
    collection `coll`. Returns the new objects."""
    import bpy
    from mathutils import Matrix

    rows = check(plan)
    skip = [n for n, _g in rows if export_skips(n)]
    for n in skip:
        print("SW adopt: left out (the web export leaves it out of every tile):", n)
    rows = [(n, g) for n, g in rows if n not in skip]
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        have = set(src.objects)
        missing = [n for n, _g in rows if n not in have]
        if missing:
            raise SystemExit(f"adopt: {len(missing)} objects not in {path.name}: {missing[:20]}")
        dst.objects = [n for n, _g in rows]
    taken = {o.name for o in bpy.data.objects}
    out = []
    for (name, g), ob in zip(rows, dst.objects, strict=True):
        if ob.hide_render or ob.hide_viewport:
            raise SystemExit(f"adopt: {name!r} is hidden in {path.name}: not in the main tiles")
        world = ob.matrix_world.copy()  # as saved: parents and constraints already applied
        coll.objects.link(ob)
        body = (g.get("text") or {}).get(name)
        if body is not None:
            if ob.type != "FONT":
                raise SystemExit(f"adopt: {name!r} takes a text but is a {ob.type}")
            if ob.data.users > 1:
                ob.data = ob.data.copy()
            f = ob.data.font
            if f and f.filepath != "<builtin>" and not f.packed_file:
                if not Path(bpy.path.abspath(f.filepath, library=f.library)).exists():
                    raise SystemExit(f"adopt: {name!r}: font file {f.filepath} not found")
            ob.data.body = body  # same font, size, extrude and material: the export converts it
        out.append((ob, name, g, world))
    bpy.context.view_layer.update()
    for ob, _name, g, _world in out:
        if g.get("transform") and _reads_other_object(ob):
            _bake(ob)  # before the move, while the cutter or input object is where it was
    for ob, name, g, world in out:
        ob.parent = None
        ob.constraints.clear()
        ob.animation_data_clear()  # no driver or action may move it back
        ob.matrix_world = Matrix(group_matrix(g.get("transform"))) @ world
        new = adopt_name(name, taken)
        taken.add(new)
        ob.name = new
        ob["adopt_source"] = name
        ob["adopt_group"] = g["name"]
        ob["adopt_file"] = path.name
    bpy.context.view_layer.update()
    # data the listed objects do not use (a parent, a cutter of a baked object) is not kept
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    print(f"SW adopt: {len(out)} objects from {path.name} ({len(skip)} left out)")
    return [o for o, *_ in out]

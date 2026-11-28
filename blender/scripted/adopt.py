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
GROUP_KEYS = {
    "name", "objects", "transform", "text", "clip", "swap_instances", "place", "materials", "fix",
    "why", "unverified",
}  # fmt: skip


def fix_target(spec):
    """A group's `fix`, "module:function" (a module under blender/), as (module, function)."""
    m = re.fullmatch(r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*):([A-Za-z_]\w*)", str(spec))
    if not m:
        raise ValueError(f"fix must be 'module:function', not {spec!r}")
    return m.group(1), m.group(2)


def export_skips(name):
    """Does the web export leave an object of this name out of every tile? Then the main tiles
    never showed it, and it is not adopted."""
    return bool(EXCL.search(name))


def _cut(text, size):
    """`text` cut to at most `size` UTF-8 bytes, never inside a character."""
    return text.encode()[:size].decode(errors="ignore")


def adopt_name(name, taken, unverified=False):
    """The build's name for source object `name`: `SW_adopt_<name>`, with `_UNVERIFIED` added when
    the group places it by inference (`unverified`). One that is too long, or already taken, is
    cut and ends with a short hash of the whole source name (the same every run), and with
    `_UNVERIFIED` when the source name carried that label (or the start of it) or the group does."""
    full = PREFIX + name
    label = "UNVERI" in name.upper()
    whole = not label or "UNVERIFIED" in name.upper()  # Blender may have cut the label already
    if unverified and not label:
        full, label = full + "_UNVERIFIED", True
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


def _inside(ring, x, y):
    hit = False
    for (ax, ay), (bx, by) in zip(ring, ring[-1:] + ring[:-1], strict=True):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def clip_drop(ring, keep, centroids):
    """For each face centroid (x, y): does a group `clip` with this ring and `keep` side drop it?"""
    return [_inside(ring, x, y) == (keep == "outside") for x, y, *_ in centroids]


def place_matrix(m):
    """A `place` entry's world matrix: 16 numbers, row-major, affine. Returns 4 rows."""
    if len(m) != 16 or not all(isinstance(v, int | float) and math.isfinite(v) for v in m):
        raise ValueError("a placed matrix is 16 numbers, row-major")
    rows = [list(m[i : i + 4]) for i in range(0, 16, 4)]
    if rows[3] != [0, 0, 0, 1]:
        raise ValueError(f"a placed matrix must end with the row 0 0 0 1, not {rows[3]}")
    return rows


def _check_extras(g, names):
    """clip, swap_instances, place and materials of a group (all optional)."""
    who = f"group {g['name']!r}"
    if "fix" in g:
        try:
            fix_target(g["fix"])
        except ValueError as e:
            raise ValueError(f"{who}: {e}") from None
    for c in g.get("clip", []):
        if c.get("keep") not in ("outside", "inside") or len(c.get("ring", [])) < 3:
            raise ValueError(f"{who}: a clip needs a ring and keep 'outside' or 'inside'")
    for a, b in (g.get("swap_instances") or {}).items():
        if not (isinstance(a, str) and isinstance(b, str) and a and b):
            raise ValueError(f"{who}: swap_instances maps collection names to collection names")
    for q in g.get("place", []):
        if not q.get("collection") or not q.get("name") or q["name"] in names:
            raise ValueError(f"{who}: a place needs a collection and a name of its own")
        names.add(q["name"])
        place_matrix(q.get("matrix", []))
    for m, new in (g.get("materials") or {}).items():
        if "name" in new and not new["name"]:
            raise ValueError(f"{who}: material {m!r}: an empty new name")
        if "colour" in new and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(new["colour"])):
            raise ValueError(f"{who}: material {m!r}: colour must be '#rrggbb'")


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
    names = set(seen)
    for g in plan["groups"]:
        _check_extras(g, names)
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


def _clip(ob, clips):
    """Delete the faces a group's `clip` rings drop (world centroids). A collection instance goes
    or stays by its origin. Returns False when nothing of `ob` is left."""
    import bmesh

    if ob.type == "EMPTY":
        o = ob.matrix_world.translation
        return not any(clip_drop(c["ring"], c["keep"], [(o.x, o.y)])[0] for c in clips)
    if ob.type != "MESH" or len(ob.modifiers):
        _bake(ob)  # the faces the export would see
    if ob.data.users > 1:
        ob.data = ob.data.copy()
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    mw = ob.matrix_world
    cs = [(mw @ f.calc_center_median()).to_tuple() for f in bm.faces]
    drop = [False] * len(cs)
    for c in clips:
        drop = [a or b for a, b in zip(drop, clip_drop(c["ring"], c["keep"], cs), strict=True)]
    kill = [f for f, d in zip(bm.faces, drop, strict=True) if d]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    left = len(bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return left > 0


def _recolour(m, new):
    """A group's `materials` entry: new name and flat colour of an adopted material."""
    if new.get("colour"):
        import kit  # noqa: PLC0415 (bpy)

        rgb = kit.srgb(new["colour"])
        m.diffuse_color = (*rgb, 1)
        if m.use_nodes and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    sock = n.inputs["Base Color"]
                    for link in list(sock.links):
                        m.node_tree.links.remove(link)
                    sock.default_value = (*rgb, 1)
    if new.get("name"):
        m.name = new["name"]


def _run_fix(g, objects, coll):
    """Call a group's `fix` (blender/<module>.py): function(objects, collection), where `objects`
    maps each source name to its adopted object; it edits them in place and returns the new
    objects it made. Anything wrong stops the build, naming the group."""
    import importlib

    import bpy

    mod, fn = fix_target(g["fix"])
    where = str(HERE.parent)
    if where not in sys.path:
        sys.path.insert(0, where)
    who = f"adopt: group {g['name']!r}: fix {g['fix']!r}"
    try:
        f = getattr(importlib.import_module(mod), fn)
    except (ImportError, AttributeError) as e:
        raise SystemExit(f"{who}: {e}") from None
    try:
        made = f(objects, coll)
    except Exception as e:  # noqa: BLE001 (any failure of the fix stops the build)
        raise SystemExit(f"{who} failed: {type(e).__name__}: {e}") from e
    made = list(made or [])
    bad = [m for m in made if not isinstance(m, bpy.types.Object)]
    if bad:
        raise SystemExit(f"{who} returned {bad[:3]}, not objects")
    print(f"SW adopt: group {g['name']!r}: {g['fix']} made {len(made)} objects")
    return made


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
    colls = sorted(
        {c for g in plan["groups"] for c in (g.get("swap_instances") or {}).values()}
        | {q["collection"] for g in plan["groups"] for q in g.get("place", [])}
    )
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        have = set(src.objects)
        missing = [n for n, _g in rows if n not in have]
        missing += [f"collection {c}" for c in colls if c not in set(src.collections)]
        if missing:
            raise SystemExit(f"adopt: {len(missing)} not in {path.name}: {missing[:20]}")
        dst.objects = [n for n, _g in rows]
        dst.collections = list(colls)  # Blender fills the list it is given with the data
    loaded = dict(zip(colls, dst.collections, strict=True))
    taken = {o.name for o in bpy.data.objects}
    out = []
    for (name, g), ob in zip(rows, dst.objects, strict=True):
        if ob.hide_render or ob.hide_viewport:
            raise SystemExit(f"adopt: {name!r} is hidden in {path.name}: not in the main tiles")
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
        out.append((ob, name, g))
    # world transforms as the main export sees them: evaluated in this scene (parents, constraints)
    bpy.context.view_layer.update()
    out = [(ob, name, g, ob.matrix_world.copy()) for ob, name, g in out]
    for ob, _name, g, _world in out:
        if g.get("transform") and _reads_other_object(ob):
            _bake(ob)  # before the move, while the cutter or input object is where it was
    for ob, name, g, world in out:
        ob.parent = None
        ob.constraints.clear()
        ob.animation_data_clear()  # no driver or action may move it back
        ob.matrix_world = Matrix(group_matrix(g.get("transform"))) @ world
        new = adopt_name(name, taken, bool(g.get("unverified")))
        taken.add(new)
        ob.name = new
        ob["adopt_source"] = name
        ob["adopt_group"] = g["name"]
        ob["adopt_file"] = path.name
        swap = (g.get("swap_instances") or {}).get(
            ob.instance_collection.name if ob.instance_collection else None
        )
        if ob.instance_type == "COLLECTION" and swap:
            ob.instance_collection = loaded[swap]
    for g in plan["groups"]:
        for q in g.get("place", []):  # new instances of a release collection, at a world matrix
            ob = bpy.data.objects.new(adopt_name(q["name"], taken), None)
            taken.add(ob.name)
            ob.instance_type = "COLLECTION"
            ob.instance_collection = loaded[q["collection"]]
            ob.matrix_world = Matrix(place_matrix(q["matrix"]))
            ob["adopt_source"] = "placed " + q["collection"]
            ob["adopt_group"] = g["name"]
            ob["adopt_file"] = path.name
            coll.objects.link(ob)
            out.append((ob, q["name"], g, None))
    bpy.context.view_layer.update()
    gone = set()
    for ob, name, g, _world in out:
        if g.get("clip") and not _clip(ob, g["clip"]):
            print("SW adopt: nothing left after the clip:", name)
            gone.add(ob.name)
    for ob, _name, g, _world in out:
        for s in getattr(ob, "material_slots", []):
            new = (g.get("materials") or {}).get(s.material.name if s.material else None)
            if new:
                _recolour(s.material, new)
    out = [r for r in out if r[0].name not in gone]
    for n in gone:
        bpy.data.objects.remove(bpy.data.objects[n])
    for g in plan["groups"]:
        if g.get("fix"):
            objects = {name: ob for ob, name, gg, _w in out if gg is g}
            for ob in _run_fix(g, objects, coll):
                if ob.name not in coll.objects:
                    coll.objects.link(ob)
                if not ob.name.startswith(PREFIX):
                    new = adopt_name(ob.name, taken)
                    taken.add(new)
                    ob.name = new
                ob["adopt_source"] = "made by " + g["fix"]
                ob["adopt_group"] = g["name"]
                ob["adopt_file"] = path.name
                out.append((ob, ob.name, g, None))
    bpy.context.view_layer.update()
    # data the listed objects do not use (a parent, a cutter of a baked object) is not kept
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    print(f"SW adopt: {len(out)} objects from {path.name} ({len(skip)} left out)")
    return [o for o, *_ in out]

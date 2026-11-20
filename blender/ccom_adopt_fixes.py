"""Fixes on objects adopted from the main model for the College of Communication and Media
(blender/scripted/ccom/adopt.json, group key "fix": "ccom_adopt_fixes:apply").

Session 20261014y lowered the east band of the main model's CCOM by pulling vertices down to the
false eave at 143.1; faces of the soffit that reached from the south wall into that band were
stretched into long diagonals (one runs across the whole south facade). They are deleted here by
height: no sound soffit face lies below its eave band.
"""

# (source object name, world z after the group transform below which faces go, why)
LOW = [
    (
        "School of Communication and Media eave soffit + fascia + rafter",
        146.6,
        "stretched faces from the 20261014y collapse; sound soffit faces lie at 146.9 to 147.5",
    ),
]


def low_faces(centroids, below):
    """Indices of the face centroids (x, y, z) that lie below `below`."""
    return [i for i, c in enumerate(centroids) if c[2] < below]


def apply(objects, collection):
    import bmesh

    for name, below, _why in LOW:
        ob = objects.get(name)
        if ob is None or ob.type != "MESH":
            continue
        if ob.data.users > 1:
            ob.data = ob.data.copy()
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        mw = ob.matrix_world
        cents = [tuple(mw @ f.calc_center_median()) for f in bm.faces]
        faces = list(bm.faces)
        gone = [faces[i] for i in low_faces(cents, below)]
        bmesh.ops.delete(bm, geom=gone, context="FACES")
        bm.to_mesh(ob.data)
        bm.free()
        print(f"ccom fix: {name}: {len(gone)} stretched faces removed")
    return []

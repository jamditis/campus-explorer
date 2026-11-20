"""Small bpy helpers shared by the southwest builders: materials, meshes, boxes, tubes, placement.

Rules the helpers enforce (see README.md in this folder):
- Object names start with `SW_`; append `_UNVERIFIED` when a size or position is inferred.
- Material names are `SW_<kind>_<name>`. The web exporter picks the viewer texture from the kind, so
the
  kind must be one of KINDS and the name must not contain another kind's word.
- A structure is a few joined meshes, one per material. No linked duplicates: the web export turns
those into
  GPU instances, which the viewer leaves out of collision and of the far tiles.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

# kind -> word that the exporter's category table (tools/web-export/export_web.py, CATS) recognises
KINDS = {
    "asphalt": "asphalt",
    "concrete": "concrete",
    "brick": "brick",
    "turf": "turf",
    "lawn": "lawn",
    "mulch": "mulch",
    "gravel": "gravel",
    "metal": "metal",
    "wood": "wood",
    "stone": "stone",
    "plaster": "stucco",
    "glass": "glass",
    "paint": "coat",
    "foliage": "foliage",
    "plastic": "plastic",
    "rubber": "rubber",
    "sign": "sign",
    "rooftile": "rooftile",
    "water": "water",
}
COLLECTION = "SW_southwest"


def collection(name=COLLECTION):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def mat(kind, name, rgb, rough=0.8, metal=0.0, alpha=1.0, emit=0.0):
    """Get or make the Principled material `SW_<kind>_<name>` (linear RGB 0..1)."""
    if kind not in KINDS:
        raise ValueError(f"unknown material kind {kind!r}; use one of {sorted(KINDS)}")
    full = f"SW_{KINDS[kind]}_{name}"
    m = bpy.data.materials.get(full)
    if m is None:
        m = bpy.data.materials.new(full)
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*rgb, 1)
        p.inputs["Roughness"].default_value = rough
        p.inputs["Metallic"].default_value = metal
        p.inputs["Alpha"].default_value = alpha
        if emit:
            p.inputs["Emission Color"].default_value = (*rgb, 1)
            p.inputs["Emission Strength"].default_value = emit
        m.diffuse_color = (*rgb, 1)
    return m


def srgb(hex_or_rgb):
    """sRGB colour ('#rrggbb' or 0..255 triple) to the linear RGB that `mat()` takes."""
    if isinstance(hex_or_rgb, str):
        h = hex_or_rgb.lstrip("#")
        hex_or_rgb = [int(h[i : i + 2], 16) for i in (0, 2, 4)]
    return tuple(
        ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
        for c in hex_or_rgb
    )


class Builder:
    """Collects geometry for one object, one material slot per material, then writes one mesh."""

    def __init__(self, name):
        if not name.startswith("SW_"):
            raise ValueError("object names start with SW_")
        if len(name) > 63:  # Blender cuts longer names, and the cut takes `_UNVERIFIED` first
            raise ValueError(f"object name longer than 63 characters: {name}")
        self.name, self.bm, self.mats = name, bmesh.new(), []

    def slot(self, material):
        if material not in self.mats:
            self.mats.append(material)
        return self.mats.index(material)

    def faces(self, verts, faces, material, smooth=False):
        """Add faces (index lists into `verts`, anticlockwise seen from outside)."""
        vs = [self.bm.verts.new(v) for v in verts]
        k = self.slot(material)
        for f in faces:
            try:
                face = self.bm.faces.new([vs[i] for i in f])
            except ValueError:
                continue  # a face on the same vertices already exists
            face.material_index = k
            face.smooth = smooth
        return vs

    def box(self, centre, size, material, angle=0.0, tilt=None):
        """Box of `size` (x, y, z) centred at `centre`, turned `angle` degrees about Z. `tilt` is an
        extra Matrix.
        """
        hx, hy, hz = (s / 2 for s in size)
        m = Matrix.Translation(Vector(centre)) @ Matrix.Rotation(math.radians(angle), 4, "Z")
        if tilt is not None:
            m = m @ tilt
        v = [
            m @ Vector((sx * hx, sy * hy, sz * hz))
            for sz in (-1, 1)
            for sy in (-1, 1)
            for sx in (-1, 1)
        ]
        self.faces(
            v,
            [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6)],
            material,
        )

    def beam(self, p0, p1, width, depth, material):
        """
        Rectangular member from p0 to p1 (any direction); `width` is horizontal, `depth` the other
        side.
        """
        a, b = Vector(p0), Vector(p1)
        d = b - a
        if d.length < 1e-6:
            return
        z = d.normalized()
        x = z.cross(Vector((0, 0, 1)))
        x = x.normalized() if x.length > 1e-6 else Vector((1, 0, 0))
        y = z.cross(x)
        v = [
            p + x * sx * width / 2 + y * sy * depth / 2
            for p in (a, b)
            for sy in (-1, 1)
            for sx in (-1, 1)
        ]
        self.faces(
            v,
            [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6)],
            material,
        )

    def tube(self, p0, p1, radius, material, sides=8, radius1=None, caps=True):
        """Round member from p0 to p1; `radius1` tapers it."""
        a, b = Vector(p0), Vector(p1)
        d = b - a
        if d.length < 1e-6:
            return
        z = d.normalized()
        x = z.cross(Vector((0, 0, 1)))
        x = x.normalized() if x.length > 1e-6 else Vector((1, 0, 0))
        y = z.cross(x)
        r1 = radius if radius1 is None else radius1
        ring = [
            (math.cos(2 * math.pi * i / sides), math.sin(2 * math.pi * i / sides))
            for i in range(sides)
        ]
        v = [a + (x * c + y * s) * radius for c, s in ring] + [
            b + (x * c + y * s) * r1 for c, s in ring
        ]
        f = [(i, (i + 1) % sides, sides + (i + 1) % sides, sides + i) for i in range(sides)]
        if caps:
            f += [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
        self.faces(v, f, material, smooth=True)

    def prism(self, ring, z0, z1, material, top=True, bottom=False):
        """Vertical extrusion of a closed anticlockwise outline [(x, y), ...] from z0 to z1."""
        n = len(ring)
        v = [(p[0], p[1], z0) for p in ring] + [(p[0], p[1], z1) for p in ring]
        f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        if top:
            f.append(tuple(range(n, 2 * n)))
        if bottom:
            f.append(tuple(range(n - 1, -1, -1)))
        self.faces(v, f, material)

    def finish(self, coll=None, weld=0.0005, recalc=True):
        """Write the mesh and link the object. Returns the object.

        `recalc` lets Blender choose each shell's outside. It guesses for loose flat panels, so a
        builder that winds every face itself (anticlockwise seen from outside) passes False.
        """
        if weld:
            bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=weld)
        if recalc:
            bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(self.name, me)
        (coll or collection()).objects.link(ob)
        return ob


def placer(at, angle_deg):
    """
    Function mapping a local point (u, v, w) to model space: u along `angle_deg` from east, v to its
    left, w up.
    """
    c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))

    def place(u, v, w=0.0):
        return (at[0] + u * c - v * s, at[1] + u * s + v * c, at[2] + w)

    return place


def preview(
    path, target, distance=60.0, azimuth=225.0, elevation=25.0, size=(1280, 800), samples=24
):
    """Render a quick Cycles check picture of the scene. Camera looks at `target` from the given
    compass side.
    """
    sc = bpy.context.scene
    az, el = math.radians(azimuth), math.radians(elevation)
    # azimuth is the compass bearing of the camera as seen from the target (0 north, 90 east)
    pos = (
        Vector(target)
        + Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
        * distance
    )
    cam = bpy.data.objects.new("SW_preview_cam", bpy.data.cameras.new("SW_preview_cam"))
    sc.collection.objects.link(cam)
    cam.location = pos
    cam.rotation_euler = (Vector(target) - pos).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_end = 5000
    sc.camera = cam
    if not any(o.type == "LIGHT" for o in sc.objects):
        sun = bpy.data.objects.new("SW_preview_sun", bpy.data.lights.new("SW_preview_sun", "SUN"))
        sun.data.energy = 3.0
        sun.data.angle = math.radians(3)
        sun.rotation_euler = (math.radians(50), 0, math.radians(200))
        sc.collection.objects.link(sun)
    if sc.world is None:
        sc.world = bpy.data.worlds.new("SW_preview_world")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.75, 0.85, 1.0, 1)
        bg.inputs[1].default_value = 0.9
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)

"""Headless Blender smoke test for CI.

Builds a tiny generated scene (ground, a lot slab, a straight curb run and a
true-arc curb return), checks the project's geometry rules on it, renders one
small Cycles CPU frame and exports a GLB the way the web viewer pipeline does.

Run: blender --background --factory-startup --python blender/smoke_test.py -- OUT_DIR
Nothing it writes is meant to be committed.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0] if argv else "smoke-out")
os.makedirs(OUT, exist_ok=True)

failures = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        failures.append(msg)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Ground and a lot slab raised above it (lot paving is only ever raised).
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.05))
lot = bpy.context.active_object
lot.name = "Lot_slab"
lot.scale = (10, 6, 0.1)
bpy.ops.object.transform_apply(scale=True)


def curb_from_points(name, pts, width=0.15, height=0.15):
    """Extrude a polyline into a simple curb mesh."""
    verts, faces = [], []
    for i, p in enumerate(pts):
        q = pts[i + 1] if i + 1 < len(pts) else p + (p - pts[i - 1])
        d = (q - p).normalized()
        n = Vector((-d.y, d.x, 0)) * (width / 2)
        for off in (n, -n):
            verts.append(p + off)
            verts.append(p + off + Vector((0, 0, height)))
    for i in range(len(pts) - 1):
        a = i * 4
        b = a + 4
        faces += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a + 1, b + 1, b + 3, a + 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


# Straight run along the lot's south edge, then a true arc (r = 3 m) return.
straight = [Vector((x, -3.1, 0.1)) for x in [-5 + i * 0.5 for i in range(21)]]
cx, cy, r = 5.0, -0.1, 3.0
arc = [
    Vector((cx + r * math.cos(t), cy + r * math.sin(t), 0.1))
    for t in [-math.pi / 2 + i * (math.pi / 2) / 16 for i in range(1, 17)]
]
curb = curb_from_points("Curb_S_straight_plus_arc", straight + arc)

# Rule: the straight run must be straight (max lateral deviation < 1 mm).
dev = max(abs(p.y - straight[0].y) for p in straight)
check(dev < 0.001, f"straight run lateral deviation {dev * 1000:.2f} mm < 1 mm")

# Rule: the arc must be a true arc (radius spread < 1 mm).
radii = [math.hypot(p.x - cx, p.y - cy) for p in arc]
check(max(radii) - min(radii) < 0.001, "arc points share one radius within 1 mm")

# Rule: lot slab top sits on or above the ground (raise-only paving).
top = max((lot.matrix_world @ v.co).z for v in lot.data.vertices)
check(top >= 0.0, f"lot slab top {top:.3f} m is not below ground")

# Camera, light, tiny Cycles CPU render.
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (14, -14, 10)
cam.rotation_euler = (math.radians(60), 0, math.radians(45))
scene.camera = cam
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sun.data.energy = 3.0  # soft light
scene.collection.objects.link(sun)
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 4
scene.render.resolution_x = 160
scene.render.resolution_y = 90
scene.render.filepath = os.path.join(OUT, "smoke.png")
bpy.ops.render.render(write_still=True)
check(os.path.getsize(scene.render.filepath) > 0, "render written")

glb = os.path.join(OUT, "smoke.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB")
check(os.path.getsize(glb) > 0, "GLB exported")

print(f"Blender {bpy.app.version_string}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)

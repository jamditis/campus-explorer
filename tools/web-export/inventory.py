# Inventory of main .blend for the web export (no evaluation; base data only)
import collections
import json
import os

import bpy

F = os.environ.get("FILE", "/workspace/nj-scenes/montclair-state/montclair_state.blend")
bpy.ops.wm.open_mainfile(filepath=F, load_ui=False)
sc = bpy.context.scene
vis = [o for o in sc.objects if not o.hide_render]
types = collections.Counter(o.type for o in vis)
mods = collections.Counter(m.type for o in vis for m in o.modifiers if m.show_render)
tri = 0
big = []
for o in vis:
    if o.type == "MESH":
        n = sum(len(p.vertices) - 2 for p in o.data.polygons)
        tri += n
        big.append((n, o.name[:60], [m.name[:30] for m in o.modifiers if m.show_render][:4]))
big.sort(reverse=True)
imgs = [(i.name, i.filepath, i.size[:], bool(i.packed_file)) for i in bpy.data.images if i.users]
mats = collections.Counter()
for o in vis:
    for s in getattr(o, "material_slots", []):
        if s.material:
            mats[s.material.name] += 1
inst = [
    (o.name[:60], o.instance_type, o.instance_collection.name if o.instance_collection else None)
    for o in vis
    if o.instance_type != "NONE"
]
gnpts = [
    (o.name[:60])
    for o in vis
    if o.type == "MESH" and len(o.data.polygons) == 0 and len(o.data.vertices) > 0
]
out = dict(
    types=types,
    mods=mods,
    tri=tri,
    big=big[:60],
    nmesh=len(big),
    imgs=imgs,
    mats=mats.most_common(300),
    inst=inst[:50],
    ninst=len(inst),
    pointclouds=gnpts[:80],
    npc=len(gnpts),
    cols=[(c.name, len(c.all_objects), c.hide_render) for c in bpy.data.collections],
)
json.dump(out, open("/workspace/nj-scenes/scripts/web/inventory.json", "w"), indent=1, default=str)
for l in open("/proc/self/status"):
    if l.startswith("VmHWM"):
        print("MEM", l.strip())
print("DONE")

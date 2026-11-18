import bpy, bmesh
from mathutils import Vector
names = [
 "UA_NormalAve_CR618_583841725_727_729_UNVERIFIED",
 "UA_CollegeAve_spur_1557427669_UNVERIFIED",
 "UA_SkylineWay_south_232846698_UNVERIFIED",
]
for name in names:
    o = bpy.data.objects.get(name)
    if not o:
        print("MISSING", name); continue
    me = o.data
    mats = [s.material.name if s.material else None for s in o.material_slots]
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    tops = [f for f in bm.faces if (o.matrix_world.to_3x3() @ f.normal).z > 0.7]
    topset = set(tops)
    bend = [e for e in bm.edges if len([f for f in e.link_faces if f in topset]) == 1]
    xs=[(o.matrix_world@v.co).x for v in me.vertices]
    ys=[(o.matrix_world@v.co).y for v in me.vertices]
    zs=[(o.matrix_world@v.co).z for v in me.vertices]
    ud = o.get("ud_fix")
    print(name, "verts", len(me.vertices), "faces", len(me.polygons), "mats", mats,
          "topF", len(tops), "topBndE", len(bend),
          "xy", round(min(xs),1), round(max(xs),1), round(min(ys),1), round(max(ys),1),
          "z", round(min(zs),2), round(max(zs),2), "ud", ud)
    # inspect color attributes
    print("  color_attrs", [a.name for a in me.color_attributes])
    print("  attrs", list(me.attributes.keys()) if hasattr(me, 'attributes') else None)
    bm.free()
o=bpy.data.objects.get("UE_Cole_east_arched_GF_UNVERIFIED")
if o:
    print("UE arches verts", len(o.data.vertices), "faces", len(o.data.polygons),
          "mats", [s.material.name if s.material else None for s in o.material_slots])
# inspect UD mat nodes
m = bpy.data.materials.get("UD_asphalt_worn_NormalAve_UNVERIFIED")
if m and m.node_tree:
    print("UD mat nodes:")
    for n in m.node_tree.nodes:
        print(" ", n.type, n.name, getattr(n, 'blend_method', None) if False else "")
    # outputs / principled
    b = m.node_tree.nodes.get("Principled BSDF")
    out = m.node_tree.nodes.get("Material Output")
    if out:
        for l in m.node_tree.links:
            if l.to_node == out:
                print("  out link from", l.from_node.name, l.from_socket.name)
    print("  blend_method", getattr(m, "blend_method", None), "surface_render_method", getattr(m, "surface_render_method", None))
print("objs", len(bpy.data.objects))

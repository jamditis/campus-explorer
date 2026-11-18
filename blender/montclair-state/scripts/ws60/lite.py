import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws60/edge_probe.py').read().split('xs=[v.co.x')[0])
def gaps():
    dg=bpy.context.evaluated_depsgraph_get(); o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); S=BVHTree.FromBMesh(bm)
    g=[]
    for e in tb.edges:
        if e.is_boundary:
            p=(e.verts[0].co+e.verts[1].co)/2; r=S.ray_cast(Vector((p.x,p.y,p.z+50)),Vector((0,0,-1)),200)
            if r[0]: g.append(p.z-r[0].z)
    import numpy as np; g=np.array(g); return len(g),round(float(np.abs(g).max()),2),int((np.abs(g)>0.5).sum()),round(float(np.median(g)),2)
print('F60 before',gaps())
print('F60 mods',[(m.name,m.type) for m in bpy.data.objects['Context_skirt_3DEP_ortho_4km'].modifiers])
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws60/feather.py').read())
bpy.context.view_layer.update(); print('F60 after',gaps())

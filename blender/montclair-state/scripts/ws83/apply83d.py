import bpy,bmesh
o=bpy.data.objects['WS83_lane_gutter_skin_asphalt_UNVERIFIED']; b=bmesh.new(); b.from_mesh(o.data)
k=[v for v in b.verts if (o.matrix_world@v.co).y< -130.2]; bmesh.ops.delete(b,geom=k,context='VERTS'); b.to_mesh(o.data); b.free()
print('WS83d removed verts',len(k),'faces now',len(o.data.polygons),flush=True)
bpy.ops.wm.save_mainfile(); print('WS83d SAVED',flush=True)

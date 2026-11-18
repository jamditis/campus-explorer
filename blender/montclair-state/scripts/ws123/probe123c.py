import bpy
d=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_doors'))
for p in d.data.polygons:
    vs=[d.matrix_world@d.data.vertices[i].co for i in p.vertices]
    print('D',p.index,[tuple(round(c,2) for c in v) for v in vs],tuple(round(c,2) for c in p.normal), p.material_index)
print('Dmat',[m.name for m in d.data.materials])
c=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_frame_canopy'))
vs=[c.matrix_world@v.co for v in c.data.vertices]
print('C bbox',[round(min(v[i] for v in vs),2) for i in range(3)],[round(max(v[i] for v in vs),2) for i in range(3)])
zs=sorted(set(round(v.z,2) for v in vs)); print('C z',zs)
with bpy.data.libraries.load('/workspace/nj-scenes/assets/campus_assets.blend',link=True) as (df,dt):
    dt.collections=['Tree_HoneyLocust_LOD1_Oct_turning']
col=dt.collections[0]
import mathutils
pts=[]
for o in col.all_objects:
    if o.type=='MESH':
        pts+= [o.matrix_world@mathutils.Vector(b) for b in o.bound_box]
print('H bbox',[round(min(v[i] for v in pts),2) for i in range(3)],[round(max(v[i] for v in pts),2) for i in range(3)], [o.name for o in col.all_objects][:6], col.instance_offset[:])

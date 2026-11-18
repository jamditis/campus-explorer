# replace faceted shared shrub meshes with a smooth leafy-lump mesh (same bbox, same materials); drop the ws108 modifiers
import bpy, bmesh
from mathutils import Vector, noise
meshes={}
for o in bpy.data.objects:
    if o.type=='MESH' and (o.name.startswith('WS99_bed_shrub_') or o.name.startswith('WS105_bank_shrub_')):
        for m in [m for m in o.modifiers if m.name.startswith('WS108_')]: o.modifiers.remove(m)
        meshes[o.data.name]=o.data
print('S108b meshes',list(meshes), 'cust', [me.has_custom_normals for me in meshes.values()])
for me in meshes.values():
    vs=[v.co.copy() for v in me.vertices]
    lo=Vector((min(v.x for v in vs),min(v.y for v in vs),min(v.z for v in vs))); hi=Vector((max(v.x for v in vs),max(v.y for v in vs),max(v.z for v in vs)))
    c=(lo+hi)/2; h=(hi-lo)/2
    bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1.0)
    for v in bm.verts:
        d=v.co.normalized(); n=noise.noise(d*2.2)*0.10+noise.noise(d*5.5)*0.05
        p=d*(1+n); p=Vector((p.x*h.x,p.y*h.y,p.z*h.z))+c
        p.z=max(p.z,lo.z+0.02); v.co=p
    mats=[m for m in me.materials]
    me.clear_geometry(); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    print('S108b',me.name,len(me.vertices),'cust',me.has_custom_normals,'mats',len(me.materials))
bpy.ops.wm.save_mainfile(); print('S108b SAVED',flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws108/render_cut108'))

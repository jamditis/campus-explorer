import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DRY=os.environ.get('DRY')=='1'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(name):
    o=bpy.data.objects[name]; me=o.evaluated_get(dg).to_mesh(); w=o.matrix_world
    return BVHTree.FromPolygons([w@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
TB=bvh('COLE_planting_beds_smooth_bu'); walks=['Footpaths_OSM','WS3_Cole_plaza_paving_20261109']
TW=[bvh(n) for n in walks+[o.name for o in bpy.data.objects if o.name.startswith('OZ_walk_joints') and o.type=='MESH']]
old=bpy.data.objects.get('WS11_Cole_SW_bed_walk_bridge_UNVERIFIED')
if old: bpy.data.objects.remove(old)
A=Vector((-86.4,-63.92,0)); B=Vector((-69.74,-68.43,0)); d=(B-A); d.z=0; d.normalize(); nrm=Vector((-d.y,d.x,0))
def ts(p): q=Vector((p.x,p.y,0))-A; return q.dot(d), q.dot(nrm)
# measure walk width from diagonal side verts (clean) and plaza side
S=[];mat=None
for n in walks:
    o=bpy.data.objects[n]; w=o.matrix_world
    for p in o.data.polygons:
        c=w@p.center
        if p.normal.z<0.7: continue
        t,s=ts(c)
        if abs(s)<3 and (17.5<t<20.5):
            for vi in p.vertices: S.append(ts(w@o.data.vertices[vi].co)[1])
            if mat is None and o.material_slots: mat=o.material_slots[p.material_index].material
smin,smax=min(S),max(S); print('WIDTH',round(smin,2),round(smax,2),'MAT',mat.name if mat else None)
tA=ts(Vector((-79.5,-66.0,0)))[0]; tB=ts(Vector((-70.6,-68.2,0)))[0]
print('T',round(tA,2),round(tB,2))
nt=max(2,int((tB-tA)/0.5)); ns=max(2,int((smax-smin)/0.5))
verts=[];faces=[]
for i in range(nt+1):
    for j in range(ns+1):
        t=tA+(tB-tA)*i/nt; s=smin+(smax-smin)*j/ns
        p=A+d*t+nrm*s; zs=[]
        for T in [TB]+TW:
            h=T.ray_cast(Vector((p.x,p.y,140)),Vector((0,0,-1)),10)
            if h[0]: zs.append(h[0].z)
        z=(max(zs) if zs else 134.48)+0.02
        verts.append(Vector((p.x,p.y,z)))
for i in range(nt):
    for j in range(ns):
        a=i*(ns+1)+j; faces.append((a,a+ns+1,a+ns+2,a+1))
print('BRIDGE',len(verts),len(faces),'zrange',round(min(v.z for v in verts),3),round(max(v.z for v in verts),3))
if not DRY:
    me=bpy.data.meshes.new('WS11_Cole_SW_bed_walk_bridge_b'); me.from_pydata(verts,[],faces); me.update()
    me.uv_layers.new(name='UVMap')
    ob=bpy.data.objects.new('WS11_Cole_SW_bed_walk_bridge_UNVERIFIED',me)
    if mat: me.materials.append(mat)
    bpy.data.objects['Footpaths_OSM'].users_collection[0].objects.link(ob)
    bpy.ops.wm.save_mainfile(); print('SAVED')

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
tA=tA-float(os.environ.get('EXT','2.0'))
print('T',round(tA,2),round(tB,2))
nt=max(2,int((tB-tA)/0.5)); ns=max(2,int((smax-smin)/0.5))
TS=[]
for n in walks:
    o=bpy.data.objects[n]; w=o.matrix_world
    for v in o.data.vertices:
        t,s_=ts(w@v.co)
        if tA-1<t<tB+1 and abs(s_)<2.6: TS.append((t,s_))
ROWS=[]
for i in range(nt+1):
    t=tA+(tB-tA)*i/nt; ss=[q[1] for q in TS if abs(q[0]-t)<0.75]
    lo=min([smin]+ss); hi=max([smax]+ss); lo=max(lo,-2.3); hi=min(hi,2.5)
    e=min(t-tA,tB-t)
    if tB-t<0.6: lo,hi=smin,smax
    hi=min(hi,float(os.environ.get('HICAP','2.2')))
    ROWS.append((lo+0.0,hi))
fo=bpy.data.objects['Footpaths_OSM']; fw=fo.matrix_world; nfix=0
for p in fo.data.polygons:
    t_,s_=ts(fw@p.center)
    if 14<t_<22 and abs(s_)<2.5 and p.material_index==1:
        nfix+=1
        if not DRY: p.material_index=0
print('SAWCUT->BROOM faces',nfix)
print('ROWS',[(round(a,2),round(b,2)) for a,b in ROWS])

verts=[];faces=[]
for i in range(nt+1):
    for j in range(ns+1):
        t=tA+(tB-tA)*i/nt; lo,hi=ROWS[i]; s=lo+(hi-lo)*j/ns
        p=A+d*t+nrm*s; zs=[]
        for T in [TB]+TW:
            h=T.ray_cast(Vector((p.x,p.y,140)),Vector((0,0,-1)),10)
            if h[0]: zs.append(h[0].z)
        e=min(t-tA,tB-t); off=0.004+0.016*min(1,max(0,(e-0.4)/1.2)); z=(max(zs) if zs else 134.48)+off
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
    print('BUILT')
if not DRY:
    oz=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']
    old=bpy.data.objects.get('WS12_bridge_slab_joints_GN_UNVERIFIED')
    if old: bpy.data.objects.remove(old)
    me=bpy.data.meshes.new('WS12_bridge_slab_joints_empty')
    j=bpy.data.objects.new('WS12_bridge_slab_joints_GN_UNVERIFIED',me)
    oz.users_collection[0].objects.link(j); j.matrix_world=oz.matrix_world.copy()
    m0=oz.modifiers[0]; m=j.modifiers.new(m0.name,'NODES'); m.node_group=m0.node_group
    for k in m0.keys():
        try: m[k]=m0[k]
        except Exception as e: print('KEYFAIL',k,e)
    m['Socket_2']=bpy.data.objects['WS11_Cole_SW_bed_walk_bridge_UNVERIFIED']
    j.update_tag(); dg2=bpy.context.evaluated_depsgraph_get(); dg2.update()
    ev=j.evaluated_get(dg2); me2=ev.to_mesh(); print('JOINTS polys',len(me2.polygons)); 
    bpy.ops.wm.save_mainfile(); print('SAVED')

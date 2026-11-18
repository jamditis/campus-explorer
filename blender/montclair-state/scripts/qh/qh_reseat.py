# qh: re-seat north-strip lamps/benches and grass points onto the (qg+qh) LiDAR ground. Lamps/benches: z shift in 'qh_dz'.
# Grass points (PC_fillet / PL_feliciano): original mesh kept as fake-user copy 'QH_bak_<name>'; REVERT=1 swaps it back.
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; GP=('PC_fillet_grass_points_UNVERIFIED','PL_feliciano_lawn_grass_points_UNVERIFIED')
for o in bpy.data.objects:
    if 'qh_dz' in o and (o.name.startswith(('Lamp_acorn','Bench_walk'))): o.location.z-=o['qh_dz']; del o['qh_dz']
for nm in GP:
    o=bpy.data.objects[nm]; bk=bpy.data.meshes.get('QH_bak_'+nm)
    if bk: old=o.data; o.data=bk; bk.name=old.name+'_tmp'; bpy.data.meshes.remove(old); bk.name=nm+'_mesh' if False else bk.name.replace('_tmp',''); bk.use_fake_user=False
if REV: print('QH reseat reverted')
else:
    dg=bpy.context.evaluated_depsgraph_get()
    def wb(names):
        V=[];P=[]
        for n in names:
            ob=bpy.data.objects.get(n)
            if not ob: continue
            e=ob.evaluated_get(dg); m=e.to_mesh(); W=ob.matrix_world; b=len(V)
            V+=[W@v.co for v in m.vertices]; P+=[tuple(b+i for i in p.vertices) for p in m.polygons]; e.to_mesh_clear()
        return BVHTree.FromPolygons(V,P)
    TB=wb(['Terrain_LiDAR_DTM_1m'])
    GB=wb(['Terrain_LiDAR_DTM_1m','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED','PB2_walk_lawn_fillet_UNVERIFIED'])
    mv=[]
    for o in bpy.data.objects:
        if not o.name.startswith(('Lamp_acorn','Bench_walk')) or o.hide_render or o.parent: continue
        x,y,z=o.matrix_world.translation
        if y<140 or y>262: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zmin=min(v.z for v in bb)
        g=GB.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if g is None: continue
        dz=g.z-0.03-zmin
        if abs(dz)>0.12: o.location.z+=dz; o['qh_dz']=dz; mv.append((o.name,round(dz,2)))
    print('QH LAMPS moved',len(mv),mv)
    for nm in GP:
        o=bpy.data.objects[nm]; me=o.data; W=o.matrix_world; Wi=W.inverted(); n=0; ds=[]
        bk=me.copy(); bk.name='QH_bak_'+nm; bk.use_fake_user=True
        for v in me.vertices:
            p=W@v.co
            if p.y<140: continue
            t=TB.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))[0]
            if t is None: continue
            d=p.z-t.z
            if abs(d)>0.3: v.co=Wi@Vector((p.x,p.y,t.z+0.01)); n+=1; ds.append(d)
        me.update(); print('QH GRASS',nm,'snapped',n, np.percentile(ds,[5,50,95]).round(2) if ds else '')
        if n==0: o.data=o.data; bpy.data.meshes.remove(bk)

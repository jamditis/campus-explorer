# ws157: UNIFY #61 Freeman N entrance block tidy.
# (a) consolidate the stacked duplicate overlay generations VD..VQ_Freeman_N_* -> keep only the newest VR_ copy of each role
#     (retire = hide + rename, nothing deleted);
# (b) clad every visible grey LiDAR-wall cell ('Freeman Hall walls' / stucco) of the entrance block (z 129.0-136.09, whole N face)
#     with the WS154 end-wall buff brick: 0.2 m ray grid along -n, quad 2 cm in front of the hit -> no blind geometry;
# (c) close-up cam on the terracotta bay top.
import bpy, bmesh, re, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
C=(W_N+W_S+E_N+E_S)/4; A=W_N; u=(E_N-W_N).normalized(); n=Vector((u.y,-u.x)); L=(E_N-W_N).length
if ((W_N+E_N)/2-C).dot(n)<0: n=-n
u3=Vector((u.x,u.y,0)); n3=Vector((n.x,n.y,0))
# (a)
vis={o.name:o for o in bpy.data.objects if not o.hide_render}
nret=0
for nm,o in list(vis.items()):
    m=re.match(r'^V([D-Q])_(Freeman_N_.*)$',nm)
    if not m or o.type!='MESH': continue
    if ('VR_'+m.group(2)) in vis:
        o.hide_render=True; o.hide_viewport=True; o.name=nm[:40]+'_RETIRED_ws157'; nret+=1
print('FIX157 retired duplicate overlay generations',nret)
# (b)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
cream=bpy.data.materials['WS154_Freeman_cream_brick_endwall_plane_UNVERIFIED']
Z0,Z1,ST=129.0,136.09,0.2
from mathutils.bvhtree import BVHTree
def sdz(p): q=Vector((p.x,p.y)); return (q-A).dot(u),(q-A).dot(n),p.z
V=[];F=[];OWN=[]
for o in bpy.data.objects:
    if o.type not in ('MESH',) or o.hide_render: continue
    bb=[sdz(o.matrix_world@Vector(c)) for c in o.bound_box]
    if max(b[0] for b in bb)<-1 or min(b[0] for b in bb)>L+1 or max(b[1] for b in bb)<-3.5 or min(b[1] for b in bb)>4.5 or max(b[2] for b in bb)<128.5 or min(b[2] for b in bb)>136.6: continue
    oe=o.evaluated_get(dg); me_=oe.to_mesh(); mw=o.matrix_world; base=len(V)
    V.extend([mw@v.co for v in me_.vertices])
    for pl in me_.polygons:
        F.append([base+i for i in pl.vertices]); mt=me_.materials[pl.material_index] if pl.material_index<len(me_.materials) else None
        OWN.append((o.name, mt.name if mt else ''))
    oe.to_mesh_clear()
print('FIX157 bvh objs',len(set(x[0] for x in OWN)),'polys',len(F))
BVH=BVHTree.FromPolygons(V,F,epsilon=0.0)
def grey(i):
    on,mn=OWN[i]
    return on=='Freeman Hall walls' or ('stucco' in mn.lower() and 'freeman' in on.lower())
bm=bmesh.new(); ncell=0; hits={}
s=-0.3
while s<L+0.3:
    z=Z0
    while z<Z1-1e-6:
        sc_=s+ST/2; zc=min(z+ST/2,Z1-0.01)
        o0=Vector((A.x,A.y,0))+u3*sc_+n3*4.0; o0.z=zc
        loc,nor,idx,dist=BVH.ray_cast(o0,-n3,8.0)
        if loc is not None and grey(idx):
            d=(Vector((loc.x,loc.y))-A).dot(n)+0.02
            if d>-3.0:
                p=lambda ss,zz: (Vector((A.x,A.y,0))+u3*ss+n3*d)+Vector((0,0,zz))
                zt=min(z+ST,Z1)
                vs=[bm.verts.new(p(s,z)),bm.verts.new(p(s+ST,z)),bm.verts.new(p(s+ST,zt)),bm.verts.new(p(s,zt))]
                f=bm.faces.new(vs); f.normal_update()
                if f.normal.dot(n3)<0: f.normal_flip()
                ncell+=1; hits[OWN[idx][0]]=hits.get(OWN[idx][0],0)+1
        z+=ST
    s+=ST
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.004)
me=bpy.data.meshes.new('WS157_Freeman_N_entrance_block_brick_infill_UNVERIFIED'); bm.to_mesh(me); bm.free(); me.materials.append(cream)
ob=bpy.data.objects.new(me.name,me)
coll=bpy.data.collections.get('WS154_Freeman_end_walls_roof_overhang_slides1965_1971_UNVERIFIED') or sc.collection
coll.objects.link(ob)
print('FIX157 infill cells',ncell,'faces',len(me.polygons),'hit objs',hits)
# (c) close-up cam on the bay top (bay s 3.3-6.6 in the probe frame ~ same order; aim at the infill centroid above z 133.5)
pts=[ob.matrix_world@v.co for v in me.vertices if v.co.z>133.5]
tgt=(sum(pts,Vector())/len(pts)) if pts else Vector((A.x,A.y,134.5))+u3*5.0
cd=bpy.data.cameras.new('WS157_CAM_closeup_Freeman_N_bay_top'); cd.lens=35
cam=bpy.data.objects.new('WS157_CAM_closeup_Freeman_N_bay_top',cd); sc.collection.objects.link(cam)
cam.location=tgt+n3*7.0+u3*2.0+Vector((0,0,-1.6)); cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
print('FIX157 cam',tuple(round(x,2) for x in cam.location),'tgt',tuple(round(x,2) for x in tgt))
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws157a.blend',copy=True)
print('SAVED_WS157A RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
walk=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS72b_Kasser_S_sidewalk')][0]
curbs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS27') and 'curb' in o.name.lower()]
print('P92 walk',walk.name,'curbs',[c.name for c in curbs])
trees=[]
for c in curbs:
    bm=bmesh.new(); bm.from_mesh(c.data); bm.transform(c.matrix_world); trees.append(BVHTree.FromBMesh(bm)); bm.free()
def near(p):
    best=None
    for t in trees:
        r=t.find_nearest(Vector((p.x,p.y,p.z)),2.0)
        if r[0] is not None and (best is None or r[3]<best[3]): best=r
    return best
mw=walk.matrix_world
bm=bmesh.new(); bm.from_mesh(walk.data)
names_ok=('WS72','WS71','WS27','WS73','WS89','COLE','Plaza','WS35','WS69','WS70')
def gap_at(p):
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,Vector((p.x,p.y,p.z+3.0)),Vector((0,0,-1)),distance=6.0)
    return hit and not any(ob.name.startswith(n) for n in names_ok), (ob.name if hit else None)
quads=[]; hits={}
for e in bm.edges:
    if not e.is_boundary: continue
    a=mw@e.verts[0].co; b=mw@e.verts[1].co
    if (a-b).length<0.02: continue
    na=near(a); nb=near(b)
    if na is None or nb is None: continue
    da=(Vector((na[0].x,na[0].y))-a.xy).length; db=(Vector((nb[0].x,nb[0].y))-b.xy).length
    if max(da,db)>1.2 or max(da,db)<0.02: continue
    m=(a+b)/2; nm=(na[0]+nb[0])/2; mid=Vector(((m.x+nm.x)/2,(m.y+nm.y)/2,m.z))
    g,obn=gap_at(mid); hits[obn]=hits.get(obn,0)+1
    if not g: continue
    def ext(p,q):
        d=Vector((q.x-p.x,q.y-p.y,0)); L=d.length
        return Vector((q.x,q.y,0))+ (d/L*0.04 if L>1e-4 else Vector()) 
    pa=ext(a,na[0]); pb=ext(b,nb[0])
    f=e.link_faces[0]; quads.append(((a.x,a.y,a.z-0.004),(b.x,b.y,b.z-0.004),(pb.x,pb.y,b.z-0.004),(pa.x,pa.y,a.z-0.004),f.material_index))
print('P92 hit-objects',hits,'quads',len(quads))
if quads and os.environ.get('SAVE')=='1':
    me=bpy.data.meshes.new('WS92_KasserS_walk_to_curb_filler_concrete')
    vs=[];fs=[]
    for q in quads:
        i=len(vs); vs+= [q[0],q[1],q[2],q[3]]; fs.append((i,i+1,i+2,i+3))
    me.from_pydata(vs,[],fs); me.update()
    for m in walk.data.materials: me.materials.append(m)
    for p,q in zip(me.polygons,quads):
        p.material_index=q[4]
        if p.normal.z<0: p.flip()
    ob=bpy.data.objects.new('WS92_KasserS_walk_to_curb_filler_concrete',me)
    for col in walk.users_collection: col.objects.link(ob)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print('P92 SAVED',len(fs))

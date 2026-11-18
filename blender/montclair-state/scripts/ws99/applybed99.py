import bpy,bmesh,json,os,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws99/bed99.json'))
O=bpy.data.objects; M=bpy.data.materials
T=O['Terrain_LiDAR_DTM_1m']; mw=T.matrix_world; imw=mw.inverted()
dg=bpy.context.evaluated_depsgraph_get(); bvh=BVHTree.FromObject(T,dg)
def gz(x,y):
    h=bvh.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400); return h[0].z
poly=B['poly']
def inside(x,y):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
V=[(x,y,gz(x,y)+0.035) for x,y in B['P']]
ref=[o for o in O if o.name.startswith('WS98_CollegeAve_bend_teardrop_island_MULCH')][0]; coll=ref.users_collection[0]
name='WS99_lotE_padS_bed_MULCH_ortho2020_LiDARshrubs_UNVERIFIED'
me=bpy.data.meshes.new(name); me.from_pydata(V,[],B['T']); me.update()
bm=bmesh.new(); bm.from_mesh(me)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bnd=[e for e in bm.edges if e.is_boundary]
r=bmesh.ops.extrude_edge_only(bm,edges=bnd)
for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.10
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
o=O.new(name,me); coll.objects.link(o); me.materials.append(ref.active_material)
o['ws99_note']='Mulch planting bed S of the WS98 raised pad, between the pad, the diagonal walk and the N-S walk; outline from the 2020 ortho (dark bed) minus modelled paving; shrubs from LiDAR non-ground clusters. Bed top terrain+3.5 cm. UNVERIFIED edges +-0.3 m.'
print('AB99 bed',len(me.vertices),len(me.polygons))
# terrain under bed lowered 5 cm
n=0
for v in T.data.vertices:
    w=mw@v.co
    if -216.6<w.x<-206.1 and -95.6<w.y<-88.3 and inside(w.x,w.y):
        w.z-=0.05; v.co=imw@w; n+=1
T.data.update(); print('AB99 terrain lowered',n)
# shrubs
src=[O[n] for n in ('shrub_036','shrub_037','shrub_038') if n in O]
random.seed(99)
for i,(x,y,h) in enumerate(B['shrubs']):
    s=random.choice(src); bh=max(0.3,s.dimensions.z/max(s.scale.z,1e-6))
    sz=h/bh; sxy=min(sz*0.85,2.3)
    so=O.new('WS99_bed_shrub_%02d_LiDARh%.1f_UNVERIFIED'%(i,h),s.data); coll.objects.link(so)
    so.location=(x,y,gz(x,y)-0.02); so.scale=(sxy,sxy,sz); so.rotation_euler=(0,0,random.uniform(0,6.28))
print('AB99 shrubs',len(B['shrubs']),[s.name for s in src])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('AB99 SAVED')

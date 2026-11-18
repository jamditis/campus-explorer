import bpy,json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED','QJ_NE_seam_fill_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    if not o: print('no',n);continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    print('OBJ',n,[round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)],len(o.data.vertices),[s.material.name if s.material else None for s in o.material_slots],[m.type+':'+m.name for m in o.modifiers])
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
for s in o.material_slots:
    m=s.material
    if m and m.node_tree:
        for nd in m.node_tree.nodes:
            print(' NODE',m.name,nd.type,nd.name,getattr(getattr(nd,'image',None),'name',None),getattr(getattr(nd,'image',None),'size',None)[:] if getattr(nd,'image',None) else '')
r=json.load(open('data/qp/rich_poly.json'))['outer']
print('RICH bbox',min(p[0] for p in r),max(p[0] for p in r),min(p[1] for p in r),max(p[1] for p in r))
# terrain edge: sample LiDAR ray hits along a grid around richardson
T=bpy.data.objects['Terrain_LiDAR_DTM_1m'];e=T.evaluated_get(dg);iw=T.matrix_world.inverted()
S=bpy.data.objects['Context_skirt_3DEP_ortho_4km'];es=S.evaluated_get(dg);iws=S.matrix_world.inverted()
row=[]
for y in range(200,360,8):
    s=''
    for x in range(0,180,6):
        h=e.ray_cast(iw@Vector((x,y,400)),Vector((0,0,-1)))[0]
        hs=es.ray_cast(iws@Vector((x,y,400)),Vector((0,0,-1)))[0]
        s+='L' if h else ('s' if hs else '.')
    print('ROW y=%d'%y,s)
for c in bpy.data.objects:
    if c.type=='CAMERA' and c.name.startswith(('QP_','QS_','QU_','QT_','QQ_')): print('CAM',c.name,tuple(round(v,1) for v in c.location))
D=json.load(open('data/scene_data.json'))
for f in D['features']:
    t=f.get('tags',{})
    p=f['pts']
    if max(q[0] for q in p)<-20 or min(q[0] for q in p)>200 or max(q[1] for q in p)<230 or min(q[1] for q in p)>420: continue
    print('FEAT',f['id'],{k:v for k,v in t.items() if k in('building','highway','name','natural','landuse','leisure','amenity','surface')},round(min(q[0] for q in p)),round(max(q[0] for q in p)),round(min(q[1] for q in p)),round(max(q[1] for q in p)))
print('NOBJ',len(bpy.data.objects))

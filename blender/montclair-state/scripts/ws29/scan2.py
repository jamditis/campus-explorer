import bpy, numpy as np, json, bmesh, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-240,70,-200,70
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def bvh(objs):
    bm=bmesh.new()
    for o in objs:
        ev=o.evaluated_get(dg)
        try: m=ev.to_mesh()
        except: continue
        if m is None: continue
        t=bmesh.new(); t.from_mesh(m); t.transform(o.matrix_world)
        tm=bpy.data.meshes.new('t'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); ev.to_mesh_clear()
    T=BVHTree.FromBMesh(bm); bm.free(); return T
def inbox(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not(max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1)
pavre=re.compile(r'(foot|road|walk|plaza|paver|asphalt|slab|crosswalk|path|drive|lot|curb|pad|apron|sidewalk|pave)',re.I)
excl=re.compile(r'(roof|wall|window|tree|grass|bench|rack|sign|lamp|letter|frame|door|glaz)',re.I)
pav=[o for o in sc.objects if o.type=='MESH' and o.visible_get() and not o.hide_render and pavre.search(o.name) and not excl.search(o.name) and inbox(o)]
bld=[o for o in sc.objects if o.type=='MESH' and o.visible_get() and re.search(r'(walls|roof)',o.name,re.I) and inbox(o)]
print('pav objs',len(pav),[o.name for o in pav][:40]); print('bld objs',len(bld))
TT=bvh([ter]); TP=bvh(pav); TB=bvh(bld)
def hz(T,x,y,top=200):
    h=T.ray_cast(Vector((x,y,top)),Vector((0,0,-1)),400); return h[0].z if h[0] else None
def inside_bld(x,y):
    h=TB.ray_cast(Vector((x,y,80)),Vector((0,0,1)),200); return h[0] is not None
# cliff cells in corridor not under buildings
S=json.load(open(R+'/data/ws29/scan.json'))
cl=[]
for x,y,c,d in S['cells']:
    if not(X0<x<X1 and Y0<y<Y1): continue
    pts=[(x+dx,y+dy) for dx in(-2,0,2) for dy in(-2,0,2)]
    nb=sum(1 for p in pts if inside_bld(*p))
    if nb>=5: continue
    cl.append((x,y,c,d,nb))
print('open-ground cliff cells in corridor',len(cl))
for r in sorted(cl,key=lambda r:-r[3])[:50]: print('OPEN',r)
# poke-through scan 0.5 m grid
poke=[]
for x in np.arange(X0,X1,0.5):
    for y in np.arange(Y0,Y1,0.5):
        zp=hz(TP,x,y)
        if zp is None: continue
        zt=hz(TT,x,y)
        if zt is None: continue
        if zp-0.02 < zt < zp+0.8: poke.append((float(x),float(y),round(zt-zp,3)))
cells={}
for x,y,d in poke:
    k=(int(x//5)*5,int(y//5)*5); c=cells.setdefault(k,[0,0]); c[0]+=1; c[1]=max(c[1],d)
print('poke samples',len(poke),'cells',len(cells))
for k,c in sorted(cells.items(),key=lambda kv:-kv[1][0])[:50]: print('POKE',k,c)
json.dump({'open':cl,'poke':poke},open(R+'/data/ws29/scan2.json','w'))

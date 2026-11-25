# W58/W57 probe: deck geometry levels, ground (evaluated) along the NJT deck S face, and model-edge surfaces
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bb(o):
    w=[o.matrix_world@Vector(c) for c in o.bound_box]; return [round(min(v.x for v in w),2),round(max(v.x for v in w),2),round(min(v.y for v in w),2),round(max(v.y for v in w),2),round(min(v.z for v in w),2),round(max(v.z for v in w),2)]
R=os.environ.get('PR','deck')
dg=bpy.context.evaluated_depsgraph_get()
deck=bpy.data.objects.get('NJ Transit Deck')
if deck and R=='deck':
    print('P241A deck bbox',bb(deck),'mods',[m.type for m in deck.modifiers],flush=True)
    me=deck.data; M=deck.matrix_world; zs={}
    for p in me.polygons:
        n=(M.to_3x3()@p.normal).normalized()
        if abs(n.z)>0.95:
            z=round((M@p.center).z,1); zs[z]=zs.get(z,0)+p.area
    print('P241A deck horiz z (area)',sorted([(z,round(a)) for z,a in zs.items() if a>50]),flush=True)
mesh=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render]
for o in mesh:
    for m in o.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get()
NB=[]
for o in mesh:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    if len(me.polygons): NB.append((o.name,BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])))
    e.to_mesh_clear()
print('P241A nobj',len(NB),[n[:40] for n,_ in NB][:80],flush=True)
G=json.loads(os.environ['GRID'])  # x0,x1,dx,y0,y1,dy
res={}
y=G[3]
while y<=G[4]+1e-6:
    x=G[0]
    while x<=G[1]+1e-6:
        hits=[]
        for n,b in NB:
            p=Vector((x,y,300))
            for _ in range(8):
                h=b.ray_cast(p,Vector((0,0,-1)))
                if h[0] is None: break
                hits.append((round(h[0].z,2),n[:36])); p=h[0]-Vector((0,0,0.002))
        hits.sort(reverse=True); res[f'{x:.0f},{y:.0f}']=hits[:14]
        x+=G[2]
    y+=G[5]
json.dump(res,open(os.environ['POUT'],'w'),indent=0)
print('P241A done',len(res),flush=True)
os._exit(0)

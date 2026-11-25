# W12c probe: all surfaces (EVALUATED for objects whose bbox covers the area) over the CCOM apron S-edge / walk fold
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=2,16,-46,-33
def bb(o):
    w=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(v.x for v in w),max(v.x for v in w),min(v.y for v in w),max(v.y for v in w)
loc=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith(('T_','Tree','WQ_','gd_','ge_')) and (lambda b: not(b[1]<X0 or b[0]>X1 or b[3]<Y0 or b[2]>Y1))(bb(o))]
loc=[o for o in loc if (lambda b:(b[1]-b[0])*(b[3]-b[2]))(bb(o))<4e6]
print('P240A objs',len(loc),[(o.name[:40],[m.type for m in o.modifiers]) for o in loc][:60],flush=True)
for o in loc:
    for m in o.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); NB=[]
for o in loc:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    if len(me.polygons): NB.append((o.name,BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])))
    e.to_mesh_clear()
res={}
y=Y0
while y<=Y1+1e-6:
    x=X0; row=[]
    while x<=X1+1e-6:
        hits=[]
        for n,b in NB:
            p=Vector((x,y,200)); 
            for _ in range(4):
                h=b.ray_cast(p,Vector((0,0,-1)))
                if h[0] is None: break
                hits.append((round(h[0].z,3),n[:34],round(h[1].z,2))); p=h[0]-Vector((0,0,0.002))
        hits.sort(reverse=True); res[f'{x:.1f},{y:.1f}']=hits[:5]
        x+=1.0
    y+=1.0
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws240/probe240a.json','w'),indent=0)
print('P240A done',len(res),flush=True)

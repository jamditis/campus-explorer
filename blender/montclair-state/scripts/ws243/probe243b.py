# ws243 seat re-check after f243a (ws243c) for the slice-5 stands/pitch (evaluated grounds, probe242g pattern) + targets for the deferred SF north cap
# walk/curb and North_NEWalkEast_gk: appended from north here, per-vertex highest evaluated ground under each vertex.
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
K=json.load(open(MS+'scripts/ws243/m2c_new243.json'))['kept']
nx=json.load(open(MS+'scripts/ws242/m2c_next242.json'))
X=[]; K=K+[n for n in nx if n.startswith('SF north cap')]
with bpy.data.libraries.load(MS+'north/montclair_north.blend',link=False) as (a,b): b.objects=[n for n in X if n in set(a.objects)]
for o in b.objects:
    if o: bpy.context.scene.collection.objects.link(o)
    for m in o.modifiers: m.show_viewport=False
bpy.context.view_layer.update()
def ev(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return t
NAMES=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('M3a_','Context_skirt','M3b_','Terrain','WS6','WS60','PK_','PZ_'))]
print('P243 grounds',NAMES,flush=True)
GR=[ev(bpy.data.objects[n]) for n in NAMES]
def gz(c):
    hh=[(t.ray_cast(Vector((c.x,c.y,c.z+20)),Vector((0,0,-1)),60)[0],nm) for t,nm in zip(GR,NAMES)]; hh=[(h.z,nm) for h,nm in hh if h is not None]
    return max(hh,default=(None,''))
out=[]
for n in K:
    o=bpy.data.objects.get(n)
    if o is None or o.type!='MESH': out.append('MISSING %s'%n); continue
    M=o.matrix_world; c0=bad=fl=0; mx=mf=0; worst=None; wf=None
    for p in o.data.polygons:
        if (M.to_3x3()@p.normal).normalized().z<0.7: continue
        c=M@p.center; c0+=1; g,gn=gz(c)
        if g is None: continue
        if g>c.z+0.01:
            bad+=1
            if g-c.z>mx: mx=g-c.z; worst=(round(c.x,1),round(c.y,1),round(c.z,2),gn[:24])
        elif c.z-g>0.25:
            fl+=1
            if c.z-g>mf: mf=c.z-g; wf=(round(c.x,1),round(c.y,1),round(c.z,2),gn[:24])
    out.append('%s up %d above %d max %.2f worst %s float %d maxfloat %.2f at %s'%(n[:44],c0,bad,mx,worst,fl,mf,wf))
T={}
for o in [x for x in b.objects if x]:
    M=o.matrix_world; d=[]; mx=0; mn=0
    for v in o.data.vertices:
        w=M@v.co; g,gn=gz(w)
        d.append(None if g is None else round(g-w.z,3))
    vals=[x for x in d if x is not None]
    T[o.name]=d
    out.append('X %s verts %d ground-minus-vert max %.2f min %.2f'%(o.name[:44],len(d),max(vals,default=0),min(vals,default=0)))
json.dump(T,open(MS+'scripts/ws243/probe243b_targets.json','w'))
open(MS+'scripts/ws243/probe243b.out','w').write('\n'.join(out)); print('P243B ok',flush=True); os._exit(0)

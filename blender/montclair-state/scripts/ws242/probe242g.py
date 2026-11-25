# m2c242 seat check: for every up-facing face of the slice-4 objects, highest evaluated ground under it (M3a/M3b/skirt/
# Terrain/WS*/PK/PZ): 'above' = ground over the face by > 1 cm (poke), 'float' = face > 0.25 m over the ground.
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
K=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws242/m2c_new242.json'))['kept']
def ev(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return t
NAMES=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('M3a_','Context_skirt','M3b_','Terrain','WS6','WS60','PK_','PZ_'))]
GR=[ev(bpy.data.objects[n]) for n in NAMES]; out=[]
for n in K:
    o=bpy.data.objects.get(n)
    if o is None or o.type!='MESH': out.append('MISSING %s'%n); continue
    M=o.matrix_world; c0=0; bad=0; fl=0; mx=0; mf=0; worst=None
    for p in o.data.polygons:
        if (M.to_3x3()@p.normal).normalized().z<0.7: continue
        c=M@p.center; c0+=1
        hh=[(t.ray_cast(Vector((c.x,c.y,c.z+20)),Vector((0,0,-1)),60)[0],nm) for t,nm in zip(GR,NAMES)]; hh=[(h.z,nm) for h,nm in hh if h is not None]; g,gn=max(hh,default=(-1e9,''))
        if g>c.z+0.01:
            bad+=1
            if g-c.z>mx: mx=g-c.z; worst=(round(c.x,1),round(c.y,1),round(c.z,2),gn[:24])
        elif c.z-g>0.25: fl+=1; mf=max(mf,c.z-g)
    out.append('%s up %d above %d max %.2f worst %s float %d maxfloat %.2f'%(n[:44],c0,bad,mx,worst,fl,mf))
open('/workspace/nj-scenes/montclair-state/scripts/ws242/probe242g.out','w').write('\n'.join(out)); print('P242G ok',flush=True); os._exit(0)

# W54: CCOM dock apron boundary vs evaluated terrain just outside it
import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ap=[o for o in bpy.data.objects if 'dock_apron' in o.name.lower() and o.type=='MESH']
print('P226K aprons',[(o.name,len(o.modifiers),len(o.data.vertices),o.data.materials[0].name if o.data.materials else None) for o in ap],flush=True)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
# other surfaces near the apron (non-terrain meshes, modifiers off), for 'what is outside'
near=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o not in ap and not o.name.startswith(('Terrain','T_','Tree')) ]
def bb(o):
    w=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(v.x for v in w),max(v.x for v in w),min(v.y for v in w),max(v.y for v in w)
for o in ap:
    M=o.matrix_world; R=M.to_3x3(); cnt={}
    for p in o.data.polygons:
        if (R@p.normal).z>0.3:
            for k in p.edge_keys: cnt[k]=cnt.get(k,0)+1
    x0,x1,y0,y1=bb(o); print('P226K',o.name,'bb',round(x0,1),round(x1,1),round(y0,1),round(y1,1),flush=True)
    loc=[n for n in near if not (bb(n)[1]<x0-2 or bb(n)[0]>x1+2 or bb(n)[3]<y0-2 or bb(n)[2]>y1+2)]
    print('P226K near objs',[n.name[:40] for n in loc][:40],flush=True)
    NB=[]
    for n in loc:
        mm=n.matrix_world; NB.append((n.name,BVHTree.FromPolygons([mm@v.co for v in n.data.vertices],[p.vertices[:] for p in n.data.polygons])))
    edges=[k for k,c in cnt.items() if c==1]
    cen=sum((M@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    for a,b in edges:
        pa=M@o.data.vertices[a].co; pb=M@o.data.vertices[b].co; mid=(pa+pb)/2
        d=(pb-pa); d.z=0
        if d.length<0.05: continue
        nrm=Vector((d.y,-d.x,0)).normalized()
        if nrm.dot(mid-cen)<0: nrm=-nrm
        res=[]
        for off in (0.15,0.5):
            q=mid+nrm*off; h=B.ray_cast(Vector((q.x,q.y,mid.z+3)),Vector((0,0,-1)))
            oth=[]
            for nn,bv in NB:
                hh=bv.ray_cast(Vector((q.x,q.y,mid.z+3)),Vector((0,0,-1)))
                if hh[0] is not None and abs(hh[0].z-mid.z)<1.0: oth.append((nn[:28],round(hh[0].z-mid.z,3)))
            res.append((off, round(h[0].z-mid.z,3) if h[0] else None, oth[:3]))
        print('P226K E',tuple(round(c,2) for c in mid),'len %.2f'%d.length,res,flush=True)
sys.stdout.flush(); os._exit(0)

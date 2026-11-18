import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get(); te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); t=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
for o in bpy.data.objects:
    if o.type!='MESH' or 'walls' not in o.name or not o.visible_get(): continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    if not vs: continue
    zmin=min(v.z for v in vs); bot=[v for v in vs if v.z<zmin+0.3]
    gaps=[]
    for v in bot[::max(1,len(bot)//40)]:
        z=tz(v.x,v.y)
        if z is not None: gaps.append(v.z-z)
    if not gaps: continue
    mx=max(gaps)
    if mx>0.4: print('FLOATWALL %-55s zmin %.1f gap max %.2f med %.2f n %d cx %.0f cy %.0f'%(o.name,zmin,mx,sorted(gaps)[len(gaps)//2],len(bot),sum(v.x for v in bot)/len(bot),sum(v.y for v in bot)/len(bot)))

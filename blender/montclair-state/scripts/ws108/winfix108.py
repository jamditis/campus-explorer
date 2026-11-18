# SELF_REVIEW 4a: drop windows whose frame corners sit inside / straddle another Chapin volume (junctions, lower roofs)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
vols=[]
for o in bpy.data.objects:
    if o.name.startswith('WS107_Chapin_') and o.type=='MESH':
        bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); vols.append(BVHTree.FromBMesh(bm)); bm.free()
def inside(p):
    for t in vols:
        n=0; q=p.copy()
        for _ in range(40):
            loc,nr,i,d=t.ray_cast(q,Vector((0,0,1)))
            if loc is None: break
            n+=1; q=loc+Vector((0,0,1e-4))
        if n%2==1: return True
    return False
w=bpy.data.objects['WS108_Chapin_windows_grid_UNVERIFIED']; me=w.data
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.normal_update()
F=bm.faces[:]; kill=set()
for k in range(0,len(F)-1,2):
    fr=F[k]; n=fr.normal
    pts=[v.co+n*0.12 for v in fr.verts]+[fr.calc_center_median()+n*0.12]
    if any(inside(p) for p in pts): kill.update([F[k],F[k+1]])
print('WF108 windows',len(F)//2,'removed',len(kill)//2)
bmesh.ops.delete(bm,geom=list(kill),context='FACES'); bm.to_mesh(me); bm.free()

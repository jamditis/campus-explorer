import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'].evaluated_get(dg)
bvh=BVHTree.FromObject(P,dg)
mw=P.matrix_world
W=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']
vs=sorted({(round(v.co.x,3),round(v.co.y,3),round(v.co.z,3)) for v in W.data.vertices})
# group into rows by x
rows={}
for x,y,z in vs: rows.setdefault(round(x,2),[]).append((y,z))
out=[]
def tz(x,y):
    h=bvh.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
    return None if h[0] is None else round(h[0].z,3)
for x in sorted(rows):
    r=sorted(rows[x]); (ya,za),(yb,zb)=r[0],r[-1]
    out.append(dict(x=x,ya=ya,za=za,yb=yb,zb=zb,
      tS=tz(x,ya-0.2),tN=tz(x,yb+0.2),tC=tz(x,(ya+yb)/2),tS1=tz(x,ya-1.0),tN1=tz(x,yb+1.0)))
x0=min(rows); 
out.append({'west_end_beyond':[tz(x0-d,405.6) for d in (0.2,0.5,1,2)]})
json.dump(out,open('data/wi/probe2.json','w'),indent=0)
for o in out: print(o)
print('MODS',[(m.name,m.thickness,m.offset) for m in W.modifiers if m.type=='SOLIDIFY'])

"""wo probe: what the scene ray hits top-down across x40-260, y140-335; WM/WJ/TL tree positions; litter mask extent."""
import bpy, json, numpy as np
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
rows=[]
for y in range(335,139,-15):
    line=[]
    for x in range(40,261,15):
        ok,loc,nrm,idx,ob,mat=sc.ray_cast(dg,Vector((x,y,500)),Vector((0,0,-1)))
        line.append((x,y,ob.name[:40] if ok else None, round(loc.z,1) if ok else None))
    rows.append(line)
names={}
for l in rows:
    for x,y,n,z in l: names[n]=names.get(n,0)+1
print('HITS',json.dumps(sorted(names.items(),key=lambda a:-a[1]),indent=0))
# grid symbol map
keys=[k for k,_ in sorted(names.items(),key=lambda a:-a[1])]
sym={k:chr(65+i) if i<26 else '?' for i,k in enumerate(keys)}
for l in rows: print(l[0][1], ''.join(sym[n] for _,_,n,_ in l))
print('LEGEND',{v:k for k,v in sym.items()})
tr={}
for o in bpy.data.objects:
    for p in ('TL_tree_','WJ_gully_tree_','WM_south_wood_tree_'):
        if o.name.startswith(p):
            t=o.matrix_world.translation; tr.setdefault(p,[]).append((round(t.x),round(t.y)))
for p,v in tr.items():
    a=np.array(v); print(p,len(v),'x',a[:,0].min(),a[:,0].max(),'y',a[:,1].min(),a[:,1].max())
print('OBJS',len(bpy.data.objects))

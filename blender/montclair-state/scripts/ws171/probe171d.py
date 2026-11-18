import bpy
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
from collections import Counter
C=Counter(); bad=[]
for i in range(0,84):
    for j in range(0,30):
        x=-345+i; y=-268-j - (x+300)*0.236*0  # grid S of the road
        y=-262.9+(x+268.8)*(-0.236)-15.5-j
        hit,loc,nor,idx,ob,_=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        if not hit: continue
        nm=ob.name.split('_LiDAR')[0][:40]
        if nm.startswith('WS171_tree') or 'tree' in nm.lower(): continue
        C[nm]+=1
        if ob.name.startswith('Context_skirt'): bad.append((x,round(y,1),round(loc.z-dz(x,y),2)))
print('PROBE171d top',C.most_common(8),flush=True); print('PROBE171d skirt',len(bad),bad[:12],flush=True)

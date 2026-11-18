import bpy, os, numpy as np
from mathutils import Vector
from collections import Counter
sc=bpy.context.scene
def zone(tag):
    dg=bpy.context.evaluated_depsgraph_get(); C=Counter(); S=Counter()
    for x in np.arange(-303,-266,0.5):
        for y in np.arange(-262,-236,0.5):
            r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
            if r[0]:
                C[r[4].name[:36]]+=1
                if r[4].name.startswith(('Context','Terrain','WS113')) or r[2].z<0.8: S[(r[4].name[:20],int(y))]+=1
    print(tag,'ZONE',C.most_common(12)); print(tag,'SUSPECT',sorted(S.items()),flush=True)
#zone('BEFORE')
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164a.py').read())
pass
OUT=os.environ.get('OUT','')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT,flush=True)

import bpy, os, numpy as np
F='/workspace/nj-scenes/montclair-state/montclair_state_ws247a.blend'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Footpaths_OSM']
o=b.objects[0]; me=o.data; M=o.matrix_world
print('FP247 mods',[(m.name,m.type) for m in o.modifiers],'mats',[m.name for m in me.materials],flush=True)
pts=[M@v.co for v in me.vertices]
sel=[p for p in pts if -240<p.x<-205 and 20<p.y<170]
import collections
c=collections.defaultdict(list)
for p in sel: c[int(p.y//5*5)].append(p.x)
for y in sorted(c): print('FP247',y,round(min(c[y]),1),round(max(c[y]),1),len(c[y]),round(np.mean([p.z for p in sel if int(p.y//5*5)==y]),2),flush=True)
os._exit(0)

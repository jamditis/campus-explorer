# ws261: WS113 fan fill faces near the crease boundary: steep (skirt) faces, smooth flag, materials; Terrain base faces there too. NO SAVE.
import bpy, os, json, numpy as np
from mathutils import Vector
B=np.array(json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws261/bnd261g.json')))
for pref in ('WS113_terrain_fan_fill_DTM1m','Terrain_LiDAR_DTM_1m'):
    o=[x for x in bpy.data.objects if x.name.startswith(pref)][0]; W=o.matrix_world; me=o.data
    st={'n':0,'steep':0,'smooth':0,'mats':{},'steep_mats':{},'zr':[]}
    for p in me.polygons:
        c=W@p.center
        if not(-227<c.x<-217 and -219<c.y<-205): continue
        d=np.hypot(B[:,0]-c.x,B[:,1]-c.y).min()
        if d>1.2: continue
        st['n']+=1; m=me.materials[p.material_index].name if me.materials else None
        st['mats'][m]=st['mats'].get(m,0)+1
        if p.use_smooth: st['smooth']+=1
        nz=(W.to_3x3()@p.normal).normalized().z
        if abs(nz)<0.7:
            st['steep']+=1; st['steep_mats'][m]=st['steep_mats'].get(m,0)+1
            vs=[(W@me.vertices[i].co).z for i in p.vertices]; st['zr'].append(round(max(vs)-min(vs),3))
    st['zr']=sorted(st['zr'])[-8:]
    print('K261',o.name[:40],st,'auto_smooth?',[m.name for m in o.modifiers][:3],flush=True)
os._exit(0)

import bpy, numpy as np, json
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
# hide trees so we see ground
skip=('tree','Tree','Leaf','band_street','shrub','Shrub')
for o in sc.objects:
    if any(s in o.name for s in skip) or o.type!='MESH': o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1,S=-195,-55,-305,-190,0.5
nx=int((X1-X0)/S); ny=int((Y1-Y0)/S)
keys={}; grid=np.zeros((ny,nx),int); Z=np.zeros((ny,nx))
for j in range(ny):
    y=Y1-(j+0.5)*S
    for i in range(nx):
        x=X0+(i+0.5)*S
        h=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
        if not h[0]: continue
        ob=h[4]; mn='?'
        try: mn=ob.data.materials[ob.data.polygons[h[3]].material_index].name
        except Exception: pass
        k=ob.name[:40]+'|'+mn
        grid[j,i]=keys.setdefault(k,len(keys)+1); Z[j,i]=h[1].z
np.save('scripts/ws140/map140_grid.npy',grid); np.save('scripts/ws140/map140_z.npy',Z)
json.dump(keys,open('scripts/ws140/map140_keys.json','w'),indent=0); print('DONE',len(keys))

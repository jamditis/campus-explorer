import bpy, numpy as np, json
D='/workspace/nj-scenes/montclair-state/'
P=np.array(json.load(open(D+'north/data/day_heroes/ct/amphi_locate_ct.json'))['osm']['232850516']['pts'])
bowl=bpy.data.objects['Kasser_amphitheater_bowl_hl']
bb=np.array([bowl.matrix_world@v.co for v in bowl.data.vertices])
x0,x1,y0,y1=bb[:,0].min(),bb[:,0].max(),bb[:,1].min(),bb[:,1].max()
print('BOWL bbox',x0,x1,y0,y1,'z',bb[:,2].min(),bb[:,2].max())
# a crude height lookup from bowl verts on a 0.25 grid
from collections import defaultdict
H={}
for p in bb:
    k=(int((p[0]-x0)/0.25),int((p[1]-y0)/0.25)); H[k]=max(H.get(k,-1e9),p[2])
def hb(x,y): return H.get((int((x-x0)/0.25),int((y-y0)/0.25)))
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE') or o.name.startswith('Kasser_amphitheater'): continue
    try:
        m=o.matrix_world; c=[m@__import__('mathutils').Vector(b) for b in o.bound_box]
    except Exception: continue
    cx=[v.x for v in c]; cy=[v.y for v in c]
    if max(cx)<x0 or min(cx)>x1 or max(cy)<y0 or min(cy)>y1: continue
    n=0;nz=0
    if o.type=='MESH' and len(o.data.vertices)<3_000_000:
        co=np.empty(len(o.data.vertices)*3); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(m); w=co@M[:3,:3].T+M[:3,3]
        sel=(w[:,0]>x0)&(w[:,0]<x1)&(w[:,1]>y0)&(w[:,1]<y1)
        for p in w[sel][:200000]:
            h=hb(p[0],p[1])
            if h is not None:
                n+=1
                if p[2]>h-0.03: nz+=1
    print('OBJ',o.name,o.type,'mods',[md.type for md in o.modifiers],'verts_over_bowl',n,'above_surface',nz, 'mat',[s.material.name if s.material else None for s in o.material_slots][:3])

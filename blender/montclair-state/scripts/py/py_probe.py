import bpy, collections
from mathutils import Vector
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5
inf=bpy.data.objects['PX_Dickson_wing_parapet_infill_UNVERIFIED']; mw=inf.matrix_world
V=[mw@v.co for v in inf.data.vertices]
xs=[v.x for v in V]; ys=[v.y for v in V]; print('INF bbox',min(xs),max(xs),min(ys),max(ys))
# top edges
ec=collections.Counter()
for p in inf.data.polygons:
    for k in p.edge_keys: ec[k]+=1
top=[k for k,c in ec.items() if c==1 and V[k[0]].z>151.29 and V[k[1]].z>151.29]
print('TOPEDGES',len(top),'len',round(sum((V[a]-V[b]).length for a,b in top),1))
# chain endpoints
deg=collections.Counter()
for a,b in top: deg[a]+=1; deg[b]+=1
ends=[V[i] for i,d in deg.items() if d==1]; print('ENDS',[(round(e.x,2),round(e.y,2)) for e in ends])
for o in bpy.data.objects:
    if o.type!='MESH' or 'ickson' not in o.name: continue
    W=[o.matrix_world@v.co for v in o.data.vertices]; Wn=[c for c in W if inwing(c)]
    if not Wn: continue
    zs=[c.z for c in Wn]
    print('OBJ',o.name,len(W),len(Wn),'z %.2f..%.2f'%(min(zs),max(zs)),[m.name for m in o.data.materials if m][:4],o.hide_render)
w=bpy.data.objects['Dickson Hall walls']; W=[w.matrix_world@v.co for v in w.data.vertices]
hi=[c for c in W if inwing(c) and c.z>151.32]
print('WALL above ZT in wing',len(hi),sorted(set((round(c.x,1),round(c.y,1),round(c.z,2)) for c in hi))[:40])
print('MATS',[m.name for m in bpy.data.materials if 'coping' in m.name.lower() or 'precast' in m.name.lower() or 'cap' in m.name.lower()])
for n in [o.name for o in bpy.data.objects if 'coping' in o.name.lower() and 'ickson' in o.name]: 
    o=bpy.data.objects[n]; print('COP',n,[m.name for m in o.data.materials if m])

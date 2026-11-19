# ws235 read-only: M3b west rail corridor census on main (modifiers off). Rail XY in y<515, ground objects overlapping the corridor.
import bpy, json
from bpy.app.handlers import persistent
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
R={}
nsr=bpy.data.collections['N_station_rail']
pts=[]
for o in nsr.all_objects:
    if o.type!='MESH' or 'Ballast' not in o.name: continue
    for v in list(o.data.vertices)[::3]:
        w=o.matrix_world@v.co
        if w.y<520: pts.append((round(w.x,1),round(w.y,1),round(w.z,2),o.name))
R['ballast']=pts
print('P235A ballast pts y<520',len(pts),flush=True)
import collections
band=collections.defaultdict(list)
for x,y,z,n in pts: band[int(y//25*25)].append(x)
for b in sorted(band): print('P235A rail band y',b,'x',min(band[b]),max(band[b]),flush=True)
G=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.polygons: continue
    cs=[c.name for c in o.users_collection]
    bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1<-470 or x0>-120 or y1<-130 or y0>520: continue
    if (x1-x0)*(y1-y0)<400: continue
    G.append((o.name,cs,round(x0),round(x1),round(y0),round(y1),len(o.data.polygons)))
for g in sorted(G,key=lambda g:-(g[3]-g[2])*(g[5]-g[4]))[:70]: print('P235A obj',g,flush=True)
json.dump(R,open('/workspace/nj-scenes/montclair-state/scripts/ws235/probe235a.json','w'))

# ws255 read-only probe: Feliciano E base course N of y 172 vs walk/ground; ground strip x -194.7..-192
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','WS250_W63','WS251_W63','WS253_W63','WS254_W63','PI_Feliciano','Feliciano School of Business walls','Footpaths_OSM','PN_Feliciano','PO_Feliciano'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
print('P255 objs',[o.name for o in b.objects],flush=True)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,box=(-205,-180,160,200)):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
others={o.name:bvh(o) for o in b.objects if o.name.startswith(('WS25','Footpaths')) and o.type=='MESH'}
def top(bt,x,y):
    if bt is None: return float('nan')
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else float('nan')
xs=[-194.6,-194.3,-194.0,-193.5,-193.0,-192.5,-192.1,-191.9,-191.0]
print('P255 cols',xs)
for y in np.arange(171.5,192.1,1.0):
    row=[]
    for x in xs:
        g=top(T,x,y); s=[(n[:12],top(t,x,y)) for n,t in others.items() if top(t,x,y)==top(t,x,y)]
        best=max([g]+[v for _,v in s if v==v]) if s else g
        who='T' if (not s or best==g) else max(s,key=lambda q:q[1] if q[1]==q[1] else -1)[0][:8]
        row.append('%.2f%s'%(best,who[:6]))
    print('P255 y%.1f '%y,' '.join(row),flush=True)
pi=bpy.data.objects['PI_Feliciano_east_base_course_UNVERIFIED']; M=pi.matrix_world; me=pi.data
print('P255 PI verts',len(me.vertices),'faces',len(me.polygons),'mods',[m.name for m in pi.modifiers],'mats',[m.name for m in me.materials if m])
pts=[M@v.co for v in me.vertices]
xs_=sorted(set(round(p.x,2) for p in pts)); print('P255 PI x values',xs_[:20], len(xs_))
for y0 in np.arange(160,200,1.0):
    q=[p for p in pts if y0<=p.y<y0+1]
    if q: print('P255 PI y%.0f n%d x %.2f..%.2f z %.2f..%.2f'%(y0,len(q),min(p.x for p in q),max(p.x for p in q),min(p.z for p in q),max(p.z for p in q)))
# sample face list N of 172
k=0
for p in me.polygons:
    ws=[M@me.vertices[i].co for i in p.vertices]
    if min(w.y for w in ws)>=172 and k<12:
        k+=1; print('P255 PIface',p.index,' '.join('(%.2f,%.2f,%.2f)'%(w.x,w.y,w.z) for w in ws))
Wo=bpy.data.objects['Feliciano School of Business walls']; bw=BVHTree.FromObject(Wo,dg)
for y in np.arange(172,196,2.0):
    h=bw.ray_cast(Vector((-185,y,137)),Vector((-1,0,0)),40); print('P255 wall y%.0f'%y, '%.2f'%h[0].x if h[0] else 'none')
os._exit(0)

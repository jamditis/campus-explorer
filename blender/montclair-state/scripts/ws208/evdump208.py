# ws208: append objects in BOX, keep Footpaths_OSM GN on, evaluate, top-object/z probe on EVALUATED meshes (0.1 m) -> json
import bpy, os, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S='/workspace/nj-scenes/montclair-state/scripts/'
B=json.load(open(S+'ws205/bbox205.json'))
x0,x1,y0,y1=map(float,os.environ['BOX'].split(','))
want=[n for n,v in B.items() if v[0]=='MESH' and not v[1] and not n.startswith(('Context_skirt','BD_farfield')) and not (v[3]<x0 or v[2]>x1 or v[5]<y0 or v[4]>y1) and v[6]<140]
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b):
    b.objects=[n for n in want if n in set(a.objects)]
sc=bpy.context.scene; KEEP=set(os.environ.get('KEEPMOD','Footpaths_OSM').split())
for o in b.objects:
    sc.collection.objects.link(o)
    if o.name not in KEEP:
        for m in o.modifiers: m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get()
T={}
for o in b.objects:
    if o.type!='MESH': continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    if len(me.polygons): T[o.name]=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    if o.name in KEEP:
        me.calc_loop_triangles(); V=np.array([tuple(mw@v.co) for v in me.vertices]); F=[tuple(t.vertices) for t in me.loop_triangles]
        sel=(V[:,0]>x0)&(V[:,0]<x1)&(V[:,1]>y0)&(V[:,1]<y1)
        np.savez('/tmp/ev208_'+o.name+'.npz',V=V,sel=sel,F=np.array(F))
    e.to_mesh_clear()
st=float(os.environ.get('STEP','0.1'))
xs=np.arange(x0,x1+1e-6,st); ys=np.arange(y1,y0-1e-6,-st); G=[]
for y in ([] if os.environ.get("NOGRID") else ys):
    row=[]
    for x in xs:
        hs=[]
        for n,t in T.items():
            h=t.ray_cast(Vector((x,y,139.5)),Vector((0,0,-1)),20)
            if h[0] is not None: hs.append((h[0].z,n))
        hs.sort(reverse=True); row.append(hs[:3])
    G.append(row)
0 if os.environ.get('NOGRID') else None
if not os.environ.get('NOGRID'): json.dump({'xs':list(map(float,xs)),'ys':list(map(float,ys)),'G':G},open(os.environ['OUTJ'],'w'))
print('EV208',len(T),flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM208',l.strip(),flush=True)

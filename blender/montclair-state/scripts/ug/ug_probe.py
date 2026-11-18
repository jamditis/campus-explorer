import bpy, json, collections
from mathutils import Vector
o=bpy.data.objects['TX Partridge entrances at OSM footway junctions (form UNVERIFIE']
print('UGP mats',[s.material.name if s.material else '-' for s in o.material_slots])
me=o.data; mw=o.matrix_world
FP=[tuple(p) for p in json.load(open('data/tx/nursing_geom.json'))['footprint']]
from mathutils.geometry import intersect_point_line
def inside(x,y):
    c=False; n=len(FP)
    for i in range(n):
        x1,y1=FP[i]; x2,y2=FP[(i+1)%n]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
# group faces by connected islands
import bmesh
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seen=set(); isl=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; cur=[]; seen.add(f.index)
    while st:
        g=st.pop(); cur.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); st.append(h)
    isl.append(cur)
for k,fs in enumerate(isl):
    vs={v for f in fs for v in f.verts}
    ps=[mw@v.co for v in vs]
    mn=[round(min(p[i] for p in ps),2) for i in range(3)]; mx=[round(max(p[i] for p in ps),2) for i in range(3)]
    c=sum(ps,Vector())/len(ps)
    mats=collections.Counter(f.material_index for f in fs)
    print('UGP isl',k,len(fs),mn,mx,'in' if inside(c.x,c.y) else 'out',dict(mats))
a=bpy.data.objects['TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)']
print('UGP apron mods',[m.type for m in a.modifiers])
l=bpy.data.objects['TY Partridge entrance steps+landings (UNVERIFIED)']
print('UGP land', l.get('UNVERIFIED'))

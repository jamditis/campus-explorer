import bpy, numpy as np, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=('KY_college_ave_carriageway','WS204_','WS70_gap_strip','ey_rhd_se_crosswalks','WS76_','WS74_cogen_lot_asphalt','WS68_RHD_ground','WS67_','LH_college')
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
T={}
for o in b.objects:
    if o.type!='MESH' or o.hide_render: continue
    mw=o.matrix_world; T[o.name]=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def tops(x,y):
    r=[]
    for n,t in T.items():
        h=t.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),60)
        if h[0] is not None: r.append((h[0].z,n))
    return sorted(r,reverse=True)
L={}
for y in np.arange(-56.6,-59.41,-0.1):
    row=''
    for x in np.arange(-260,-255.4,0.1):
        r=tops(x,y); n=r[0][1] if r else '-'
        L.setdefault(n,chr(97+len(L))); row+=L[n]
    print('M205b %6.1f %s'%(y,row))
print('M205b',L)
for x,y in [(-258,-57.4),(-257,-57.6),(-257.5,-57.9),(-259,-57.3),(-256.8,-58.0)]:
    print('M205b',x,y,[(round(z,3),n[:30]) for z,n in tops(x,y)][:4])

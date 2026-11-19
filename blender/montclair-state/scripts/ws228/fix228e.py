# W53d apron (ws228, after fix228a/c/d): with the terrain's east edge now on dtm_1m, the WS60 edge apron's long column quads
# (x 246 -> 276, one quad per column spanning y -248.74..-33.5) still interpolate their OLD end heights, so beyond the edge the
# apron rose up to ~3.5 m as a bank (A1-corner close-up). Rebuild that apron strip as a grid: rows at every inner-edge vertex
# (the 2 m fix228a splits), columns at the inner edge, x 253.5/261/268.5 and the outer edge x~276; heights blend linearly from
# the inner edge (= terrain edge, dtm_1m) to the outer edge (unchanged: linear between its two existing end verts, so the
# farfield join is unchanged). Only faces with every vertex at x >= 245.9 and y <= -33.45 are replaced (faces must also reach y < -40, so the 1 m rows near
# y -35..-26 are left alone). UVs from a least-squares affine fit of the replaced faces' own UVs. Same material.
import bpy, bmesh, json
import numpy as np
from mathutils import Vector
o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; ab=bmesh.new(); ab.from_mesh(o.data)
uvl=list(ab.loops.layers.uv.items())
F=[f for f in ab.faces if all(v.co.x>=245.9 and v.co.y<=-33.45 for v in f.verts) and any(v.co.y<-40 for v in f.verts)]
assert F, 'no apron faces'
mi=F[0].material_index; sm=F[0].smooth
X=[];U={nm:[] for nm,L in uvl}
for f in F:
    for l in f.loops:
        X.append([l.vert.co.x,l.vert.co.y,1.0])
        for nm,L in uvl: U[nm].append([l[L].uv.x,l[L].uv.y])
X=np.array(X); fit={nm:np.linalg.lstsq(X,np.array(U[nm]),rcond=None)[0] for nm in U}
res={nm:float(np.abs(X@fit[nm]-np.array(U[nm])).max()) for nm in U}
inner=sorted([v for v in set(v for f in F for v in f.verts) if v.co.x<246.5],key=lambda v:v.co.y)
outer=sorted([v for v in set(v for f in F for v in f.verts) if v.co.x>275.5],key=lambda v:v.co.y)
o0,o1=outer[0],outer[-1]
def outz(y): t=(y-o0.co.y)/(o1.co.y-o0.co.y); return o0.co.z*(1-t)+o1.co.z*t, o0.co.x*(1-t)+o1.co.x*t
FV=set(v for f in F for v in f.verts)
bmesh.ops.delete(ab,geom=F,context='FACES_ONLY')
for e in [e for e in ab.edges if e.is_valid and not e.link_faces and (e.verts[0] in FV or e.verts[1] in FV)]: ab.edges.remove(e)
keep=set(inner)|{o0,o1}
for v in [v for v in FV if v.is_valid and not v.link_edges and v not in keep]: ab.verts.remove(v)
COLS=[253.5,261.0,268.5]
rows=[]
for v in inner:
    y=v.co.y; zo,xo=outz(y); r=[v]
    for cx in COLS:
        s=(cx-v.co.x)/(xo-v.co.x); r.append(ab.verts.new(Vector((cx,y,v.co.z*(1-s)+zo*s))))
    if v is inner[0]: r.append(o0)
    elif v is inner[-1]: r.append(o1)
    else: r.append(ab.verts.new(Vector((xo,y,zo))))
    rows.append(r)
nf=0
for a,b in zip(rows[:-1],rows[1:]):
    for j in range(len(a)-1):
        try: f=ab.faces.new([a[j],a[j+1],b[j+1],b[j]])
        except ValueError: continue
        f.material_index=mi; f.smooth=sm; nf+=1
        if f.normal.z<0: f.normal_flip()
        for l in f.loops:
            c=l.vert.co
            for nm,L in uvl:
                uv=np.array([c.x,c.y,1.0])@fit[nm]; l[L].uv=(float(uv[0]),float(uv[1]))
ab.to_mesh(o.data); ab.free(); o.data.update()
rep={'replaced_faces':len(F),'inner_rows':len(inner),'new_quads':nf,'uv_fit_maxres':{k:round(v,4) for k,v in res.items()}}
print('F228E',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws228/fix228e_report.json','w'))

# ws219 W38 retry: depressed (flush) curb at the College Ave crosswalk by the Kasser landing / RHD SE corner.
# The WS69 gap-strip curb ends as a 13-16 cm stub where landing (WS72) and gap asphalt (WS67) already meet flush
# (probe218e). fix218c failed because the curb's end segment had only 2 top verts within 1.5 m. Here: isolate the curb
# island at the stub, bisect it with planes perpendicular to its axis every 0.25 m over the last 1.75 m, then taper the
# top verts to adjacent paving + 1 cm at the end (full height 1.5 m back). Curb-only; no paving raised/lowered.
# Transition length 1.5 m = typical NJDOT/ADA depressed-curb transition at a crosswalk; exact length UNVERIFIED.
import bpy, bmesh, json, math
from mathutils import Vector
G=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws218/w38_grid218.json'))
G={tuple(map(float,k.split(','))):v for k,v in G.items()}
o=bpy.data.objects['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']; M=o.matrix_world; Mi=M.inverted()
E=Vector((-254.75,-53.35)); R=1.5
def ground(x,y):
    c=[v[1] for (gx,gy),v in G.items() if abs(gx-x)<=0.6 and abs(gy-y)<=0.6 and not v[0].startswith('WS69')]
    return min(c) if c else None
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
W=lambda v:(M@v.co)
v0=min(bm.verts,key=lambda v:(W(v).xy-E).length)
print('F219A nearest vert',tuple(round(c,2) for c in W(v0)),round((W(v0).xy-E).length,2),flush=True)
# island by linked edges
isl={v0}; st=[v0]
while st:
    v=st.pop()
    for e in v.link_edges:
        w=e.other_vert(v)
        if w not in isl: isl.add(w); st.append(w)
near=[W(v) for v in isl if (W(v).xy-E).length<4.0]
print('F219A island verts',len(isl),'near',len(near),flush=True)
c=sum((p.xy for p in near),Vector((0,0)))/len(near)
sxx=sum((p.x-c.x)**2 for p in near); syy=sum((p.y-c.y)**2 for p in near); sxy=sum((p.x-c.x)*(p.y-c.y) for p in near)
ang=0.5*math.atan2(2*sxy,sxx-syy); d=Vector((math.cos(ang),math.sin(ang)))
# orient d so that the stub end is the max projection among near verts
tv=[(p.xy-E).dot(d) for p in near]
if abs(min(tv))<abs(max(tv)): d=-d; tv=[-t for t in tv]  # stub end = the island end nearest E (crosswalk side)
tend=max(tv); print('F219A axis',tuple(round(x,3) for x in d),'tend',round(tend,2),'tmin',round(min(tv),2),flush=True)
# bisect island geometry (local space plane) at tend-0.25k
geom=set(isl)
for v in isl:
    geom.update(v.link_edges); geom.update(f for f in v.link_faces)
d3=Vector((d.x,d.y,0)); nloc=(Mi.to_3x3()@d3).normalized()
for k in range(1,8):
    pw=Vector((E.x,E.y,125.3))+d3*(tend-0.25*k)
    res=bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=Mi@pw,plane_no=nloc,dist=0.005)
    geom.update(res['geom_cut']); geom=set(g for g in geom if g.is_valid)
    for g in list(res['geom_cut']):
        if isinstance(g,bmesh.types.BMVert): geom.update(g.link_edges); geom.update(g.link_faces)
isl2=set(g for g in geom if isinstance(g,bmesh.types.BMVert))
n=0; zs=[]
for v in isl2:
    w=W(v); s=tend-(w.xy-E).dot(d)
    if s>R or s<-0.05: continue
    gz=ground(w.x,w.y)
    if gz is None or w.z<gz+0.02: continue
    t=max(0.0,s)/R; nz=gz+0.01+(w.z-gz-0.01)*(t*t*(3-2*t))
    if nz<w.z-0.001:
        zs.append((round(s,2),round(w.z,3),round(nz,3))); w.z=nz; v.co=Mi@w; n+=1
bm.to_mesh(o.data); bm.free(); o.data.update()
print('F219A verts in island after cut',len(isl2),'tapered',n,sorted(zs)[:12],flush=True)

# ws220 fix220b: College Ave curb jog E of the RHD SE / Kasser landing corner (x -249.4..-248.4, y -56.2..-52.9).
# The WS69 N gap-strip curb ended at (-249.4,-56.1) and the WS27 curb_left began 3.2 m further N at (-248.4,-53.0);
# along the jog between them the road met the WS70 grass wedge and the WS72 landing with no curb (14 cm raw step,
# landing edge bulging 0.2-0.6 m over the road). Fix: (1) one curb-return piece along the road edge joining the two
# curb ends (same concrete, same top heights, reveal ~13 cm, bottom 0.25 m under the road); (2) WS72 landing edge
# verts in front of the curb back line pulled back onto it (xy only, z kept); (3) WS70 grass behind the new curb
# RAISED to curb top - 3 cm where lower (raise-only, AGENTS rule 6). Curb path follows the evaluated road edge
# (ws220 eprobe grid); exact real kerb line UNVERIFIED (2020 ortho too coarse at 2048 px).
import bpy, bmesh, math
from mathutils import Vector
if bpy.data.objects.get('WS220_CollegeAve_curb_jog_return_UNVERIFIED'): raise SystemExit('F220B already')
CP=[(-249.38,-56.12),(-249.02,-55.98),(-248.86,-55.5),(-248.80,-54.8),(-248.72,-54.0),(-248.60,-53.32),(-248.38,-52.95)]
Z0,Z1=125.81,125.83; W=0.17; DEP=0.38
def cr(p0,p1,p2,p3,t):
    return tuple(0.5*((2*p1[i])+(-p0[i]+p2[i])*t+(2*p0[i]-5*p1[i]+4*p2[i]-p3[i])*t*t+(-p0[i]+3*p1[i]-3*p2[i]+p3[i])*t**3) for i in range(2))
P=[CP[0]]+CP+[CP[-1]]; S=[]
for k in range(1,len(P)-2):
    for j in range(6): S.append(cr(P[k-1],P[k],P[k+1],P[k+2],j/6))
S.append(CP[-1])
L=[0.0]
for a,b in zip(S,S[1:]): L.append(L[-1]+math.dist(a,b))
bm=bmesh.new(); rings=[]; BACK=[]
for i,(x,y) in enumerate(S):
    a=S[max(0,i-1)]; b=S[min(len(S)-1,i+1)]; dx,dy=b[0]-a[0],b[1]-a[1]; n=math.hypot(dx,dy); dx,dy=dx/n,dy/n
    nx,ny=dy,-dx   # right side = road
    zt=Z0+(Z1-Z0)*L[i]/L[-1]
    rf=(x+nx*W/2,y+ny*W/2); bk=(x-nx*W/2,y-ny*W/2)
    r=[bm.verts.new((rf[0],rf[1],zt-DEP)),bm.verts.new((rf[0],rf[1],zt-0.012)),bm.verts.new((rf[0]-nx*0.012,rf[1]-ny*0.012,zt)),bm.verts.new((bk[0],bk[1],zt)),bm.verts.new((bk[0],bk[1],zt-DEP))]
    rings.append(r); BACK.append((bk,(-nx,-ny),zt))
for r0,r1 in zip(rings,rings[1:]):
    for k in range(5):
        bm.faces.new((r0[k],r0[(k+1)%5],r1[(k+1)%5],r1[k]))
bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
bm.normal_update(); 
me=bpy.data.meshes.new('WS220_CollegeAve_curb_jog_return_UNVERIFIED'); bm.to_mesh(me); bm.free()
for f in me.polygons: f.use_smooth=False
o=bpy.data.objects.new(me.name,me); me.materials.append(bpy.data.materials['WS27_curb_concrete_UNVERIFIED'])
ref=bpy.data.objects['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']
for c in ref.users_collection: c.objects.link(o)
# outward-normal check
me.calc_loop_triangles() if hasattr(me,'calc_loop_triangles') else None
cen=sum((v.co for v in me.vertices),Vector())/len(me.vertices)
print('F220B curb verts',len(me.vertices),'faces',len(me.polygons),'len m',round(L[-1],2),flush=True)
# back line incl. WS27 curb_left back edge W part
cl=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; M=cl.matrix_world
def backpt(p):
    best=None
    for (bx,by),(ox,oy),zt in BACK:
        d=math.hypot(p[0]-bx,p[1]-by)
        if best is None or d<best[0]: best=(d,(bx,by),(ox,oy),zt)
    return best
# (2) landing pull-back
ld=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; MI=ld.matrix_world.inverted(); MW=ld.matrix_world
mv=0
for v in ld.data.vertices:
    w=MW@v.co
    if not (-249.6<=w.x<=-247.2 and -55.2<=w.y<=-53.0): continue
    d,(bx,by),(ox,oy),zt=backpt((w.x,w.y))
    # ox,oy points from road to back (away from road); road side if (w-b).(o) < 0
    s=(w.x-bx)*ox+(w.y-by)*oy
    if s<0 and d<1.0:
        w2=Vector((bx,by,w.z)); v.co=MI@w2; mv+=1
# also verts in front of curb_left (x>-248.4): use curb_left back = road face + 0.21 along +y-ish; pull to curb_left top back
for v in ld.data.vertices:
    w=MW@v.co
    if not (-248.4<w.x<=-247.0 and -53.8<=w.y<=-53.0): continue
    # curb_left road face y at x (from probe): y_rf = -53.05 + (w.x+248.4)*(-0.272)
    yb=-53.05+(w.x+248.4)*(-0.272)+0.19
    if w.y<yb: v.co=MI@Vector((w.x,yb,w.z)); mv+=1
ld.data.update(); print('F220B landing verts pulled',mv,flush=True)
# (3) WS70 grass raise behind the new curb
g=bpy.data.objects['WS70_gap_strip_grass_berms']; GM=g.matrix_world; GI=GM.inverted(); nr=0
for v in g.data.vertices:
    w=GM@v.co
    if not (-250.4<=w.x<=-248.2 and -56.4<=w.y<=-52.9): continue
    d,(bx,by),(ox,oy),zt=backpt((w.x,w.y)); s=(w.x-bx)*ox+(w.y-by)*oy
    if s>=-0.05 and d<1.3 and w.z<zt-0.03:
        w.z=zt-0.03-0.02*max(0,d-0.6); v.co=GI@w; nr+=1
g.data.update(); print('F220B WS70 verts raised',nr,flush=True)

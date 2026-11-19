# ws220 fix220c (Codex review on PR #16):
# (P1) rebuild the W39 curb return as true geometry: arc (left) -> straight run -> arc (right), equal radii solved from
#      the two curb ends and their headings, instead of a Catmull-Rom spline; landing edge + grass re-fitted to the new
#      back line. (P2) outward face normals (bmesh recalc on the closed mesh). (P2) Lot 38 paint mask image renamed to
#      ws220c_mask_tile_0.png so tools/web-export picks it up (tile list data/ws220c_mask_tiles.json, 5-field).
import bpy, bmesh, math
from mathutils import Vector
im=bpy.data.images.get('ws220c_mask_SF_0.png')
if im:
    im.name='ws220c_mask_tile_0.png'  # packed; filepath left alone (re-pathing a packed image triggers a re-pack)
    print('F220C image renamed',flush=True)
old=bpy.data.objects.get('WS220_CollegeAve_curb_jog_return_UNVERIFIED')
cols=list(old.users_collection) if old else list(bpy.data.objects['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED'].users_collection)
if old: me0=old.data; bpy.data.objects.remove(old); bpy.data.meshes.remove(me0)
W=0.17; DEP=0.38; Z0,Z1=125.81,125.83
# start: WS69 N curb end cap centre + heading (from WS69 verts 0.4-1.6 m back along the curb)
C0=Vector((-249.385,-56.125)); C1=Vector((-248.38,-52.95))
w69=bpy.data.objects['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']; M=w69.matrix_world
# N curb only (WS69 also holds the S curb): its W-end ring sits 3.39 m back at (-252.39,-54.55)
near=[ (M@v.co).xy for v in w69.data.vertices if 3.0<((M@v.co).xy-C0).length<3.45 and (M@v.co).y>-57.0 ]
cb=sum(near,Vector((0,0)))/len(near); h0=(C0-cb).normalized()
print('F220C WS69 verts used',len(near),flush=True)
h1=Vector((0.965,-0.262)).normalized()   # WS27 curb_left heading at its W end (probe220c)
t0=math.atan2(h0.y,h0.x); t1=math.atan2(h1.y,h1.x); tm=math.pi/2  # straight run heads north
# left arc t0->tm, straight north s, right arc tm->t1, both radius r:  C1-C0 = r*A + (0,s)
A=Vector(((math.sin(tm)-math.sin(t0))+(math.sin(tm)-math.sin(t1)), (math.cos(t0)-math.cos(tm))+(math.cos(t1)-math.cos(tm))))
D=C1-C0; r=D.x/A.x; s=D.y-r*A.y
print('F220C heading0 %.1f deg heading1 %.1f deg radius %.3f straight %.3f'%(math.degrees(t0),math.degrees(t1),r,s),flush=True)
assert r>0.2 and s>0, 'bad fit'
PTS=[]  # (x,y,heading)
def arcL(c,ta,tb,n):
    for k in range(n+1):
        t=ta+(tb-ta)*k/n; yield (c.x+r*math.sin(t)-r*math.sin(ta)*0, t)
p=C0.copy(); 
n1=10
for k in range(n1+1):
    t=t0+(tm-t0)*k/n1; PTS.append((C0.x+r*(math.sin(t)-math.sin(t0)), C0.y+r*(math.cos(t0)-math.cos(t)), t))
P1=Vector(PTS[-1][:2])
ns=max(2,int(s/0.25))
for k in range(1,ns+1): PTS.append((P1.x,P1.y+s*k/ns,tm))
P2=Vector(PTS[-1][:2])
for k in range(1,n1+1):
    t=tm+(t1-tm)*k/n1; PTS.append((P2.x+r*(math.sin(tm)-math.sin(t)), P2.y+r*(math.cos(t)-math.cos(tm)), t))
print('F220C end error m',round((Vector(PTS[-1][:2])-C1).length,4),flush=True)
L=[0.0]
for a,b in zip(PTS,PTS[1:]): L.append(L[-1]+math.dist(a[:2],b[:2]))
bm=bmesh.new(); rings=[]; BACK=[]
for i,(x,y,t) in enumerate(PTS):
    nx,ny=math.sin(t),-math.cos(t)   # right of heading = road side
    zt=Z0+(Z1-Z0)*L[i]/L[-1]
    rf=(x+nx*W/2,y+ny*W/2); bk=(x-nx*W/2,y-ny*W/2)
    rings.append([bm.verts.new((rf[0],rf[1],zt-DEP)),bm.verts.new((rf[0],rf[1],zt-0.012)),bm.verts.new((rf[0]-nx*0.012,rf[1]-ny*0.012,zt)),bm.verts.new((bk[0],bk[1],zt)),bm.verts.new((bk[0],bk[1],zt-DEP))])
    BACK.append((bk,(-nx,-ny),zt))
for r0,r1 in zip(rings,rings[1:]):
    for k in range(5): bm.faces.new((r0[k],r0[(k+1)%5],r1[(k+1)%5],r1[k]))
bm.faces.new(rings[0]); bm.faces.new(rings[-1])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
me=bpy.data.meshes.new('WS220_CollegeAve_curb_jog_return_UNVERIFIED'); bm.to_mesh(me); bm.free()
up=sum(1 for f in me.polygons if f.normal.z>0.5); dn=sum(1 for f in me.polygons if f.normal.z<-0.5)
cen=sum((v.co for v in me.vertices),Vector())/len(me.vertices)
outw=sum(1 for f in me.polygons if (f.center-cen).dot(f.normal)>0)
print('F220C curb verts',len(me.vertices),'faces',len(me.polygons),'up',up,'down',dn,'outward',outw,'len',round(L[-1],2),flush=True)
o=bpy.data.objects.new(me.name,me); me.materials.append(bpy.data.materials['WS27_curb_concrete_UNVERIFIED'])
for c in cols: c.objects.link(o)
def backpt(p):
    best=None
    for i in range(len(BACK)-1):
        (a,_,za),(b,_,zb)=BACK[i],BACK[i+1]; a=Vector(a); b=Vector(b); ab=b-a; tt=max(0,min(1,(p-a).dot(ab)/ab.length_squared)); q=a+ab*tt
        d=(p-q).length; nrm=Vector(BACK[i][1])
        if best is None or d<best[0]: best=(d,q,nrm,za+(zb-za)*tt)
    return best
ld=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; MW=ld.matrix_world; MI=MW.inverted(); mv=0
for v in ld.data.vertices:
    w=MW@v.co
    if not (-249.6<=w.x<=-248.2 and -55.2<=w.y<=-53.0): continue
    d,q,nrm,zt=backpt(w.xy); sgn=(w.xy-q).dot(nrm)   # >0 = behind the curb (away from road)
    if sgn<0 or d<0.12: v.co=MI@Vector((q.x,q.y,w.z)); mv+=1
ld.data.update(); print('F220C landing verts fitted',mv,flush=True)
g=bpy.data.objects['WS70_gap_strip_grass_berms']; GM=g.matrix_world; GI=GM.inverted(); nr=0
for v in g.data.vertices:
    w=GM@v.co
    if not (-250.4<=w.x<=-248.0 and -56.4<=w.y<=-52.9): continue
    d,q,nrm,zt=backpt(w.xy); sgn=(w.xy-q).dot(nrm)
    if sgn>=-0.05 and d<1.3 and w.z<zt-0.03:
        w.z=zt-0.03-0.02*max(0,d-0.6); v.co=GI@w; nr+=1
g.data.update(); print('F220C WS70 verts raised',nr,flush=True)

# ws215 W35: street-level sidewalk E of the Red Hawk deck College Ave vehicle apron, back of the road curb -> SE stair-tower face.
# Evidence: Joe's Sep 2021 Street View (refs/joe) shows a street-level concrete walk to the SE core doors; plan from 2020 ortho + model faces.
# One solid slab (0.45 m deep so its S face reads as the curb face), top = road N edge + 0.15 m + 1.5 % cross-fall up to the building.
# Removes: KY_rhd_drive_side_walk_fill (warped strip), LH gutter faces lying on the lawn / sunk 2.4 m under the road inside x -268..-255.5.
# WS68 lawn verts under the slab clamped 5 cm below its top.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
KY=ob('KY_college_ave_carriageway_asphalt ('); AP=ob('KX_drive_apron'); LH=ob('LH_college_ave_gutter_asphalt_fill'); W68=ob('WS68_RHD_ground_northDTM')
LF=ob('LF_rhd_se_curb_ramp_fill'); WF=ob('KY_rhd_drive_side_walk_fill'); LAND=ob('bx2_rhd_se_core_entry_landing')
def bvh(o): M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
tk=bvh(KY)
def roadz(x):
    for y in (-49.25,-49.4,-49.6,-49.9,-50.3,-50.8,-51.5):
        h=tk.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None: return h[0].z
    return None
YS=-49.55   # back of road curb (KY N edge -49.0 + gutter/curb 0.55 m; ortho curb line)
XW,XE=-265.1,-255.55   # apron E edge .. WS72 Kasser landing W edge
YB=-46.35   # SE core skin face (y min -46.2..-46.3 incl. reveal)
XC=-263.2   # core W corner; W of it the walk runs N to the deck S face
YN=-43.35
# sample the road edge every 0.5 m, then fit a straight line (no wobble)
xs=[XW+i*0.5 for i in range(int((XE-XW)/0.5)+1)]
pts=[(x,roadz(x)) for x in xs]; pts=[p for p in pts if p[1] is not None]
print('F215 KY',KY.name[:40],len(KY.data.polygons),'hits',len(pts),flush=True)
n=len(pts); mx=sum(p[0] for p in pts)/n; mz=sum(p[1] for p in pts)/n
k=sum((p[0]-mx)*(p[1]-mz) for p in pts)/sum((p[0]-mx)**2 for p in pts)
def top(x,y): return mz+k*(x-mx)+0.15+0.015*(y-YS)
print('F215 road fit n',n,'mean',round(mz,3),'slope',round(k,4),'top W/E',round(top(XW,YS),3),round(top(XE,YS),3),flush=True)
ta=bvh(AP)
def hit(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0]
# road N edge (northmost KY hit) per x, straight-line fit
E=[]
for x in [XW+0.3+i*0.5 for i in range(19)]:
    for i in range(0,120):
        y=-45.0-i*0.1
        if hit(tk,x,y) is not None: E.append((x,y)); break
def fit(P):
    n=len(P); mx=sum(p[0] for p in P)/n; my=sum(p[1] for p in P)/n
    kk=sum((p[0]-mx)*(p[1]-my) for p in P)/sum((p[0]-mx)**2 for p in P); return lambda u: my+kk*(u-mx)
ysf=fit(E) if len(E)>3 else (lambda u: YS)
# apron E edge (eastmost apron hit) per y
A=[]
for y in [YS-1.5+i*0.5 for i in range(int((YN-YS+1.5)/0.5)+1)]:
    for i in range(0,60):
        x=-262.0-i*0.1
        if hit(ta,x,y) is not None: A.append((y,x)); break
A=[p for p in A if p[0]>=-50.0]
print('F215 apronE',[(round(a,1),round(b,2)) for a,b in A],flush=True)
_xf=fit(A) if len(A)>3 else (lambda u: XW)
XMIN=max(b for a,b in A) if A else XW
xwf=lambda u: max(_xf(max(u,-50.0)),XMIN-0.6) if u<-50.0 else _xf(u)
print('F215 roadN pts',len(E),'y@W/E',round(ysf(XW),2),round(ysf(XE),2),'apronE pts',len(A),'x@S/N',round(xwf(ysf(XW)),2),round(xwf(YN),2),flush=True)
ZW=mz+k*(XW-mx)+0.15; ZE=125.05
def top(x,y): return ZW+(ZE-ZW)*(x-XW)/(XE-XW)+0.01*(y-ysf(x))
def poly():
    sw=(xwf(ysf(XW)),ysf(xwf(ysf(XW)))); se=(XE,ysf(XE)); ne=(XE,YB); c1=(XC,YB); c2=(XC,YN); nw=(xwf(YN),YN)
    return [sw,se,ne,c1,c2,nw]
PL=poly()
def inside(x,y):
    c=False; n=len(PL)
    for i in range(n):
        x1,y1=PL[i]; x2,y2=PL[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
bm=bmesh.new()
def patch(P00,P10,P11,P01,nu,nv):
    G={}
    for i in range(nu+1):
        for j in range(nv+1):
            u=i/nu; v=j/nv
            x=(1-u)*(1-v)*P00[0]+u*(1-v)*P10[0]+u*v*P11[0]+(1-u)*v*P01[0]
            y=(1-u)*(1-v)*P00[1]+u*(1-v)*P10[1]+u*v*P11[1]+(1-u)*v*P01[1]
            G[i,j]=bm.verts.new((x,y,top(x,y)))
    for i in range(nu):
        for j in range(nv): bm.faces.new([G[i,j],G[i+1,j],G[i+1,j+1],G[i,j+1]])
sw,se,ne,c1,c2,nw=PL
nwb=(xwf(YB),YB)
patch(sw,se,ne,nwb,40,14)
patch(nwb,c1,c2,nw,8,12)
bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=0.01)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
ext=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:])
for v in [e for e in ext['geom'] if isinstance(e,bmesh.types.BMVert)]: v.co.z-=0.45
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
me=bpy.data.meshes.new('WS215_RHD_SE_sidewalk'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=False
mat=bpy.data.materials.get('Kasser_apron_concrete_cm') or bpy.data.materials.get('KX2_walk_concrete.001')
me.materials.append(mat)
SW215=bpy.data.objects.new('WS215_RHD_SE_core_street_level_sidewalk_streetview2021_UNVERIFIED_width',me)
(LF.users_collection[0] if LF else bpy.context.scene.collection).objects.link(SW215)
# UV for the concrete texture (planar, 1 unit = 1 m)
uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
    c=me.vertices[l.vertex_index].co; uv.data[l.index].uv=(c.x*0.5,c.y*0.5)
# remove the warped walk strip (replaced by the slab)
if WF:
    for c in list(WF.users_collection): c.objects.unlink(WF)
    print('F215 unlinked',WF.name,flush=True)
# LH gutter faces: delete faces in the slab footprint, and faces sunk >0.3 m under the road in x -268..-255.5
nd=0
if LH:
    M=LH.matrix_world; bm=bmesh.new(); bm.from_mesh(LH.data); bm.faces.ensure_lookup_table(); kill=[]
    for f in bm.faces:
        c=M@f.calc_center_median()
        if not (-268.5<c.x<-255.5 and -54<c.y<-43): continue
        if c.y>YS-0.05: kill.append(f); continue
        h=tk.ray_cast(Vector((c.x,c.y,200)),Vector((0,0,-1)),300)
        if h[0] is None or c.z<h[0].z-0.3: kill.append(f)
    nd=len(kill); bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(LH.data); bm.free(); LH.data.update()
# lawn under the slab
nc=0
if W68:
    me=W68.data; M=W68.matrix_world; Mi=M.inverted()
    for v in me.vertices:
        w=M@v.co
        if inside(w.x,w.y) and w.z>top(w.x,w.y)-0.05: v.co=Mi@Vector((w.x,w.y,top(w.x,w.y)-0.05)); nc+=1
    me.update()
print('F215 a slab faces',len(me.polygons) if False else len(SW215.data.polygons),'LH faces deleted',nd,'WS68 clamped',nc,'landing z',[round((LAND.matrix_world@v.co).z,3) for v in LAND.data.vertices][:4] if LAND else None,flush=True)

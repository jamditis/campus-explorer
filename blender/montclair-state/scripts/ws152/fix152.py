# ws152 UNIFY #58 (found in the ws152 review renders of fix151): (A) the triangle N of the WS151 apron between the Freeman NE
# forecourt, the N aisle and Skyline Way rendered as LAWN, but 2023 LiDAR class-2 intensity there is 2.6-3.0k (= asphalt; lawn
# here is 7-13k) with a smooth ~6 % fall S from the aisle -> it is paving (Skyline Way's N end opening onto the aisle).
# (B) with the false OSM kerb gone, a dark seam shows along the Lot 9 / Skyline Way junction S of the apron (y -205.8..-191.3):
# cover it with the same overlap-and-fade apron. Footpaths_OSM faces lying on asphalt-intensity cells in box A are deleted.
import bpy, bmesh, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
D=np.load(M+'scripts/ws142/dtm142.npy'); X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fx=(x-X0)/R; fy=(Y1-y)/R; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i; Z=D[1]
    return (Z[i,j]*(1-tx)+Z[i,j+1]*tx)*(1-ty)+(Z[i+1,j]*(1-tx)+Z[i+1,j+1]*tx)*ty
def inten(x,y): return D[2][int(round((Y1-y)/R)),int(round((x-X0)/R))]
sp2=json.load(open(M+'scripts/ws151/curbs_osm.json'))['2']
c2=sorted([(p[1],p[0]) for p in sp2 if -215<p[1]<-160 and p[0]<-58])
def xe(y): return float(np.interp(y,[a for a,b in c2],[b for a,b in c2]))-0.05
dg=bpy.context.evaluated_depsgraph_get()
def bvh_of(objs,box):
    b=bmesh.new()
    for o in objs:
        oe=o.evaluated_get(dg)
        try: me=oe.to_mesh()
        except Exception: continue
        if me is None: continue
        t=bmesh.new(); t.from_mesh(me); t.transform(o.matrix_world)
        x0,x1,y0,y1=box
        dead=[f for f in t.faces if not any(x0-2<v.co.x<x1+2 and y0-2<v.co.y<y1+2 for v in f.verts)]
        bmesh.ops.delete(t,geom=dead,context='FACES'); m2=bpy.data.meshes.new('tmp152'); t.to_mesh(m2); t.free(); b.from_mesh(m2); bpy.data.meshes.remove(m2); oe.to_mesh_clear()
    T=BVHTree.FromBMesh(b); b.free(); return T
def hz(T,x,y):
    h=T.ray_cast(Vector((x,y,140.0)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
UNDER_P=('WS142_Lot9_asphalt','WS135a_Skyline_Way_asphalt','WS150_Lot9_E_apron_S','WS145_walk_nose_lot_asphalt','WS151_Lot9_E_apron_unified')
HARD_P=('WS143_Freeman_NE_forecourt','WS143_Freeman_E_concrete_band','WS147_','WS142_Lot9_W_curb','WS145_','WS141_')
# Footpaths faces on asphalt cells in box A
fp=bpy.data.objects.get('Footpaths_OSM')
if fp:
    bm=bmesh.new(); bm.from_mesh(fp.data); mw=fp.matrix_world; kill=[]
    for f in bm.faces:
        c=mw@f.calc_center_median()
        if -71.5<c.x<-62 and -179<c.y<-169 and inten(c.x,c.y)<4000: kill.append(f)
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(fp.data); bm.free(); fp.data.update(); print("FIX152_FOOTPATHS_DELETED",len(kill))
def apron(name,x0,x1f,y0,y1,fade,maskA):
    box=(x0,-61.0,y0,y1)
    under=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name=='Roads_OSM' or o.name.startswith(UNDER_P))]
    hard=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(HARD_P) and not o.name.startswith(('WS145_walk_nose_lot_asphalt',))]
    TU=bvh_of(under,box); TH=bvh_of(hard,box)
    offs=[hz(TU,x,y)-dz(x,y) for x in np.arange(x0+0.3,x1f(y0)-0.3,0.7) for y in np.arange(y0+0.3,y1,0.7) if hz(TU,x,y) is not None]
    OFF=float(np.median(offs)) if offs else 0.04; print("FIX152_OFF",name[:30],round(OFF,3),len(offs))
    G=0.25; me=bpy.data.meshes.new(name); bm=bmesh.new(); V={}
    xs=np.arange(x0,-61.0,G); ys=np.arange(y0,y1+1e-6,G)
    def gv(i,k):
        if (i,k) not in V: V[(i,k)]=bm.verts.new((min(xs[i],x1f(ys[k])),ys[k],0.0))
        return V[(i,k)]
    nf=0
    for i in range(len(xs)-1):
        for k in range(len(ys)-1):
            cx,cy=xs[i]+G/2,ys[k]+G/2
            if not (xs[i]<x1f(ys[k])-0.02 and xs[i]<x1f(ys[k+1])-0.02): continue
            if maskA and inten(cx,cy)>=4000: continue
            if hz(TH,cx,cy) is not None: continue
            q=[gv(i,k),gv(i+1,k),gv(i+1,k+1),gv(i,k+1)]
            if len({v.co.to_tuple() for v in q})==4: bm.faces.new(q); nf+=1
    for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
    for v in bm.verts:
        x,y=v.co.x,v.co.y; tgt=dz(x,y)+OFF; ex=hz(TU,x,y)
        d=min(x-x0, x1f(y)-x, y-y0, y1-y); w=max(0.0,min(1.0,d/fade))
        base=ex if ex is not None else tgt; z=(1-w)*base+w*tgt
        if ex is not None: z=max(z,ex+0.004)
        v.co.z=z
    for it in range(4):
        nz={}
        for v in bm.verts:
            if v.is_boundary: continue
            nb=[e.other_vert(v).co.z for e in v.link_edges]; nz[v]=0.5*v.co.z+0.5*sum(nb)/len(nb)
        for v,z in nz.items():
            ex=hz(TU,v.co.x,v.co.y); v.co.z=max(z,ex+0.004) if ex is not None else z
    ed=[e for e in bm.edges if e.is_boundary]; r=bmesh.ops.extrude_edge_only(bm,edges=ed)
    for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.08
    bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new(name,me)
    ref=[o for o in bpy.data.objects if o.name.startswith('WS142_Lot9_asphalt')][0]
    for c in ref.users_collection: c.objects.link(ob)
    me.materials.append(bpy.data.materials['Asphalt'])
    print("FIX152_APRON",name[:40],"faces",nf)
    tr=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=tr.matrix_world; tmi=tm.inverted(); n=0
    TA=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    for v in tr.data.vertices:
        w_=tm@v.co
        if x0-0.3<w_.x<-61.0 and y0-0.3<w_.y<y1+0.3:
            h=TA.ray_cast(Vector((w_.x,w_.y,140)),Vector((0,0,-1)))[0] or TA.ray_cast(Vector((w_.x+0.3,w_.y,140)),Vector((0,0,-1)))[0] or TA.ray_cast(Vector((w_.x-0.3,w_.y,140)),Vector((0,0,-1)))[0]
            if h is not None and w_.z>h.z-0.08: w_.z=h.z-0.08; v.co=tmi@w_; n+=1
    tr.data.update(); print("FIX152_TERRAIN_LOWERED",n)
    return ob
apron('WS152_Lot9_N_triangle_asphalt_Skyline_N_end_LiDAR2023int_UNIFY58',-71.0,xe,-178.95,-169.5,1.0,True)
apron('WS152_Lot9_Skyline_junction_seam_cover_LiDAR2023_UNIFY58',-68.9,lambda y:min(-66.3,xe(y)),-205.8,-191.25,0.6,False)

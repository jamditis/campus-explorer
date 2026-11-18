# ws68 (Nov 11 2026 ~3 PM ET): Joe's 2:25/2:26 PM clipping fixes around the Red Hawk Deck import.
# 1) new 1 m ground patch WS68_RHD_ground_northDTM (north/data/grid_1m.npz dtm_filled; B23/B17 LiDAR) over x -345..-248.6, y -135..40,
#    replacing the coarse 4 km skirt + raised WS60 apron there ("land bridge"); feathered to the skirt on W/S/N edges, blended to main terrain at x -249;
#    clamped 8 cm under every road/paving object and under the deck footprint; skirt/apron verts in the domain pushed 0.4 m under the patch.
# 2) crosswalk stripes ey_rhd_se_crosswalks: faces off the road removed, the rest seated 1.5 cm on the road surface.
# 3) removed duplicate north ground pieces: gb_panzer_footprint_underpatch, ce_rhd_wall_apron (blurry north-ortho ground).
# 4) gb_cogen_paving / fn_rhd_aisle_asphalt re-seated 4 cm over the patch (drape) so no wedges stand proud.
import bpy,bmesh,numpy as np,os,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def O(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o,ev=True):
    e=o.evaluated_get(dg) if ev else o; m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
def hit(t,x,y,top=300):
    h=t.ray_cast(Vector((x,y,top)),Vector((0,0,-1)))[0]; return h.z if h else None
g=np.load('/workspace/nj-scenes/montclair-state/north/data/grid_1m.npz'); D=g['dtm_filled']
def dtm(x,y):
    fx=x+600-0.5; fy=y+260-0.5; i=int(math.floor(fx)); j=int(math.floor(fy)); a=fx-i; b=fy-j
    return float((D[j,i]*(1-a)+D[j,i+1]*a)*(1-b)+(D[j+1,i]*(1-a)+D[j+1,i+1]*a)*b)
SK=O('Context_skirt_3DEP_ortho_4km'); AP=O('WS60_terrain_edge_apron'); TE=O('Terrain_LiDAR_DTM_1m')
# skirt base surface (no modifiers) for the feather target
skt=bvh(SK,ev=False); apb=bvh(AP,ev=False); ter=bvh(TE)
PAVE=['KX_drive_apron','KY_college_ave_carriageway','KY_rhd_drive_side_walk','LF_rhd_se_curb_ramp','LH_college_ave_gutter','WS67_CollegeAve_gap','WS27_CollegeAve_carriageway','WS27_CollegeAve_curb','cf_kasser_rhd_joint','bx2_rhd_se_core_entry_landing','eu_rhd_ground_slab','fn_rhd_aisle_asphalt','gb_cogen_paving']
pav=[bvh(o) for o in bpy.data.objects if any(o.name.startswith(p) for p in PAVE)]
# deck footprint (OSM 312849085) via deck mass bbox test with raycast on the deck object at low z
deck=bvh(O('Red Hawk Deck')); slab=bvh(O('eu_rhd_ground_slab'))
X0,X1,Y0,Y1,F=-345.0,-248.6,-135.0,40.0,8.0
xs=np.arange(X0,X1+0.01,1.0); xs[-1]=X1; ys=np.arange(Y0,Y1+0.01,1.0)
bm=bmesh.new(); V={}
fn_drape={}
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        z=dtm(x,y)
        w=min(1,max(0,min(x-X0,y-Y0,Y1-y)/F))  # 0 at W/S/N edge
        s=hit(skt,x,y); sa=hit(apb,x,y)
        if sa is not None: s=max(s or -1e9,sa)
        if s is not None: z=s*(1-w)+z*w
        if x>-255:  # blend to main terrain edge
            t=hit(ter,min(x,-249.3),y)
            if t is not None:
                k=min(1,(x+255)/6.0); z=z*(1-k)+(t-0.05)*k
        hs_=hit(slab,x,y,160)
        if hs_ is not None: z=min(z,hs_-0.08)  # deck ground slab: always under it (dtm_filled humps inside the footprint)
        for p in pav:
            h=hit(p,x,y,160)
            if h is not None and h>z-3: z=min(z,h-0.08)
        V[i,j]=bm.verts.new((x,y,z))
for j in range(len(ys)-1):
    for i in range(len(xs)-1):
        bm.faces.new((V[i,j],V[i+1,j],V[i+1,j+1],V[i,j+1]))
# UVs: same planar mapping as the skirt (fit from the skirt mesh)
sm=SK.data; uvl=sm.uv_layers['ortho'].data; A=[];U=[]
for pi_ in range(0,len(sm.polygons),7):
    poly=sm.polygons[pi_]
    for li in poly.loop_indices:
        co=SK.matrix_world@sm.vertices[sm.loops[li].vertex_index].co; A.append((co.x,co.y,1)); U.append(tuple(uvl[li].uv))
A=np.array(A);U=np.array(U); cu,_,_,_=np.linalg.lstsq(A,U[:,0],rcond=None); cv,_,_,_=np.linalg.lstsq(A,U[:,1],rcond=None)
res=np.abs(A@cu-U[:,0]).max(); print('A68 uv fit max err',res)
uv=bm.loops.layers.uv.new('ortho')
NORTH_ORTHO=os.environ.get('NORTH_ORTHO','1')=='1'
for f in bm.faces:
    for l in f.loops:
        c=l.vert.co
        l[uv].uv=((c.x+600)/820,(c.y+260)/1660) if NORTH_ORTHO else (cu[0]*c.x+cu[1]*c.y+cu[2], cv[0]*c.x+cv[1]*c.y+cv[2])
me=bpy.data.meshes.new('WS68_RHD_ground_northDTM'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
pt=bpy.data.objects.new('WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ortho)',me)
if NORTH_ORTHO:
    # ws68b: same NJ 2020 ortho as main, from the north file's wider export (x -600..220, y -260..1400, 0.405 m/px), in a copy of main's ground material
    gm=bpy.data.materials['Ground_ortho_grass'].copy(); gm.name='WS68_Ground_ortho_grass_north2020'
    img=bpy.data.images.load('/workspace/nj-scenes/montclair-state/north/data/ortho2020_north.jpg',check_existing=True)
    for n in gm.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('ortho2020'): n.image=img; n.extension='EXTEND'
    me.materials.append(gm)
else:
    for m in SK.data.materials: me.materials.append(m)
TE.users_collection[0].objects.link(pt)
dg.update(); ptb=bvh(pt,ev=False)
# copy skirt attributes used by the material (if any, as constant defaults) -> list them
print('A68 skirt attrs',[a.name for a in SK.data.attributes if not a.name.startswith('.')])
# densify the coarse skirt faces that touch the domain so its surface can be pushed under the patch
bm=bmesh.new(); bm.from_mesh(SK.data); mw=SK.matrix_world
def ind(c,pad=2): return X0-pad<=c.x<=X1+pad and Y0-pad<=c.y<=Y1+pad
fs=[f for f in bm.faces if any(ind(mw@v.co) for v in f.verts) or ind(mw@f.calc_center_median())]
# also faces that contain domain corners/interior though no vert is inside: test a 5 m probe grid
from mathutils.bvhtree import BVHTree as BT
tb=BT.FromBMesh(bm); extra=set()
for yy in np.arange(Y0,Y1+1,5):
    for xx in np.arange(X0,X1+1,5):
        loc,nor,idx,dd=tb.ray_cast(mw.inverted()@Vector((xx,yy,400)),Vector((0,0,-1)))
        if idx is not None: extra.add(idx)
bm.faces.ensure_lookup_table(); fs=list(set(fs)|{bm.faces[i] for i in extra})
es=list({e for f in fs for e in f.edges}); print('A68 skirt faces densified',len(fs),'edges',len(es))
bmesh.ops.subdivide_edges(bm,edges=es,cuts=12,use_grid_fill=True)
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
bm.to_mesh(SK.data); bm.free(); SK.data.update()
# push skirt + apron verts in the domain under the patch
for ob in (SK,AP):
    n=0; mw=ob.matrix_world; mi=mw.inverted()
    for v in ob.data.vertices:
        c=mw@v.co
        if X0-0.5<=c.x<=X1+0.2 and Y0-0.5<=c.y<=Y1+0.5:
            hs=[hit(ptb,c.x+dx,c.y+dy) for dx in (-2.5,0,2.5) for dy in (-2.5,0,2.5)]; hs=[q for q in hs if q is not None]
            h=min(hs) if hs else None
            if h is not None and c.z>h-0.5: v.co=mi@Vector((c.x,c.y,h-0.5)); n+=1
    ob.data.update(); print('A68 lowered',ob.name[:30],n)
# 3) delete duplicate north ground pieces
for nm in ('gb_panzer_footprint_underpatch','ce_rhd_wall_apron'):
    o=O(nm); print('A68 delete',o.name); bpy.data.objects.remove(o)
# 4) drape cogen paving / aisle asphalt on the patch where they float or sink
for nm in ('gb_cogen_paving','fn_rhd_aisle_asphalt'):
    o=O(nm); mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0
    for v in o.data.vertices:
        c=mw@v.co; h=hit(ptb,c.x,c.y)
        if h is None: continue
        d=c.z-(h+0.04)
        if abs(d)>0.03: mx=max(mx,abs(d)); v.co=mi@Vector((c.x,c.y,h+0.04)); n+=1
    o.data.update(); print('A68 draped',nm,n,'max move %.2f'%mx)
# 2) crosswalk stripes: keep faces whose centre is over a road surface, seat on it
roads=[bvh(o) for o in bpy.data.objects if any(o.name.startswith(p) for p in ('KY_college_ave_carriageway','WS67_CollegeAve_gap','WS27_CollegeAve_carriageway','LH_college_ave_gutter','LF_rhd_se_curb_ramp','fn_rhd_aisle_asphalt'))]
def road(x,y):
    hs=[h for h in (hit(r,x,y,140) for r in roads) if h is not None]; return max(hs) if hs else None
cw=O('ey_rhd_se_crosswalks'); mw=cw.matrix_world; mi=mw.inverted()
bm=bmesh.new(); bm.from_mesh(cw.data); kill=[]
for f in bm.faces:
    c=mw@f.calc_center_median()
    if road(c.x,c.y) is None: kill.append(f)
bmesh.ops.delete(bm,geom=kill,context='FACES'); nk=len(kill)
for v in bm.verts:
    c=mw@v.co; h=road(c.x,c.y)
    if h is None: h=road(c.x+0.05,c.y) or road(c.x,c.y+0.05) or c.z-0.015
    v.co=mi@Vector((c.x,c.y,h+0.015))
bm.to_mesh(cw.data); bm.free(); cw.data.update(); print('A68 crosswalk faces removed',nk,'left',len(cw.data.polygons))
# trees in the domain: seat on ground
for o in bpy.data.objects:
    if o.name.startswith('T_') and o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; cx=sum(b.x for b in bb)/8; cy=sum(b.y for b in bb)/8; zmin=min(b.z for b in bb)
        if X0<cx<X1 and Y0<cy<Y1:
            h=hit(ptb,o.matrix_world.translation.x,o.matrix_world.translation.y); print('A68 tree',o.name,round(cx,1),round(cy,1),'zmin',round(zmin,2),'ground',h and round(h,2))
dg.update(); skv=bvh(SK); bad=0; tot=0
for yy in np.arange(Y0+0.5,Y1,2.0):
    for xx in np.arange(X0+0.5,X1,2.0):
        a=hit(ptb,xx,yy); b=hit(skv,xx,yy)
        if a is None or b is None: continue
        tot+=1
        if b>a+0.05:
            bad+=1
            if bad<12: print('A68 over',round(xx,1),round(yy,1),round(b-a,2))
print('A68 skirt-over-patch samples',bad,'of',tot)
print('A68 patch verts',len(me.vertices),'faces',len(me.polygons))
if os.environ.get('SAVE'): bpy.ops.wm.save_mainfile(); print('A68 saved')

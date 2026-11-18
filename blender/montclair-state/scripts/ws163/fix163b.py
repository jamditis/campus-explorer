# ws163b: the coarse 3DEP context skirt sits 0.3-0.5 m ABOVE the LiDAR ground W of x -268 (probe ws163a) and hid the new Normal Ave W extension.
# (1) visible 1 m LiDAR ground patch W of the WS110 patch (x -348..-300, y -279..-232): lawn, asphalt inside OSM Lot 36 (487498693; base surface only, markings not modelled)
# (2) hidden skirt target = patch + WS110 patch (box) + WS163 surfaces, attr wv_in=0.10
# (3) GN modifier (copy of WV_skirt_under_stone_west, FACE-domain selection, subdivide 5) drops the skirt 12 cm under the topmost target
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=os.environ.get('OUT',''); OB=bpy.data.objects
P='/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/'
D=np.load(P+'dtm163.npy')[0].copy(); X0,Y0,R=-350.0,-290.0,0.5
for j,i in zip(*np.nonzero(np.isnan(D))):
    for rr in range(1,14):
        sub=D[max(j-rr,0):j+rr+1,max(i-rr,0):i+rr+1]
        if np.isfinite(sub).any(): D[j,i]=float(np.nanmedian(sub)); break
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
col=bpy.data.collections['WS163_NormalAve_W_LotS']
for n in ('WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED','WS163_skirt_target_hidden'):
    if OB.get(n): OB.remove(OB[n])
surf=[o for o in col.objects if o.type=='MESH']+[o for o in OB if o.name.startswith('WS162_') and o.type=='MESH']
V=[];F=[]
for o in surf:
    b=len(V); V+=[o.matrix_world@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
T=BVHTree.FromPolygons(V,F)
def ztop(x,y):
    best=None
    for ddx,ddy in ((0,0),(0.4,0),(-0.4,0),(0,0.4),(0,-0.4)):
        h=T.ray_cast(Vector((x+ddx,y+ddy,200)),Vector((0,0,-1)))
        if h[0] is not None: best=h[0].z if best is None else min(best,h[0].z)
    return best
L36=[(-331.95,-221.31),(-337.99,-241.83),(-321.92,-246.28),(-315.45,-219.46),(-320.2,-218.57),(-325.85,-221.97)]
def pip(poly,x,y):
    ins=False; n=len(poly)
    for k in range(n):
        x1,y1=poly[k]; x2,y2=poly[(k+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: ins=not ins
    return ins
# Lot 3 W walk band / lot occupy x>-312 for y>-236: keep the patch out of there (stop at y -236 east of x -312)
bm=bmesh.new(); XS=np.arange(-348,-299.49,1.0); YS=np.arange(-279,-231.9,1.0); G={}
for x in XS:
    for y in YS:
        z=dz(x,y)-0.03; zt=ztop(x,y)
        if zt is not None: z=min(z,zt-0.06)
        G[(x,y)]=bm.verts.new((x,y,z))
lawn=bpy.data.materials.get('COLE_lawn_post2020_bs'); asm=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho')
for x in XS[:-1]:
    for y in YS[:-1]:
        cx,cy=x+0.5,y+0.5
        if cx>-312 and cy>-236.5: continue
        f=bm.faces.new((G[(x,y)],G[(x+1,y)],G[(x+1,y+1)],G[(x,y+1)])); f.material_index=1 if pip(L36,cx,cy) else 0
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED'); bm.to_mesh(me); bm.free(); me.materials.append(lawn); me.materials.append(asm)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.25,p.y*0.25)
patch=OB.new(me.name,me); col.objects.link(patch); print('PATCH faces',len(me.polygons))
# hidden target
tb=bmesh.new()
srcs=[patch]+surf+[o for o in OB if o.name.startswith('WS110_ground_patch_S_of_y-238')]
for o in srcs:
    mw=o.matrix_world
    for p in o.data.polygons:
        cs=[mw@o.data.vertices[i].co for i in p.vertices]
        if all(-352<c.x<-266 and -282<c.y<-228 for c in cs): tb.faces.new([tb.verts.new(c) for c in cs])
tm=bpy.data.meshes.new('WS163_skirt_target_hidden'); tb.to_mesh(tm); tb.free()
a=tm.attributes.new('wv_in','FLOAT','POINT'); a.data.foreach_set('value',[0.10]*len(tm.vertices))
tgt=OB.new('WS163_skirt_target_hidden',tm); col.objects.link(tgt); tgt.hide_render=True; tgt.hide_viewport=True; print('TARGET faces',len(tm.polygons))
# GN
sk=OB['Context_skirt_3DEP_ortho_4km']
for m in [m for m in sk.modifiers if m.name.startswith('WS163_')]: sk.modifiers.remove(m)
ng=bpy.data.node_groups['WV_skirt_under_stone_west'].copy(); ng.name='WS163_skirt_under_normalave_W'
N=ng.nodes
N['Compare'].inputs[1].default_value=-362.0; N['Compare.001'].inputs[1].default_value=-262.0
N['Compare.002'].inputs[1].default_value=-292.0; N['Compare.003'].inputs[1].default_value=-218.0
N['Separate Geometry'].domain='FACE'; N['Subdivide Mesh'].inputs['Level'].default_value=5
N['Object Info'].inputs['Object'].default_value=tgt; N['Named Attribute'].inputs['Name'].default_value='wv_in'
mod=sk.modifiers.new('WS163_skirt_under_normalave_W','NODES'); mod.node_group=ng
# keep it right after the other skirt_under modifiers (before nothing else matters); probe
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x,y in ((-330,-252),(-320,-254),(-300,-259),(-290,-262),(-309,-242),(-340,-270),(-330,-238)):
    r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1))); print('PROBE',x,y,r[4].name[:45] if r[0] else None,round(r[1].z,2) if r[0] else None)
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)

# ws113: replace the Terrain_LiDAR corner-fan triangles (hub vert 0 at (-245.1,-248.1) etc.) SE of the College Ave S end
# with a 1 m DTM grid patch; patch is clamped under paving tops by the WS113 GN (all paving in the area).
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
SAVE=os.environ.get('SAVE','main')
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    i=min(max(i,0),DT.shape[0]-2); j=min(max(j,0),DT.shape[1]-2)
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
# orientation check: which index order matches the terrain mesh?
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
co=np.array([v.co[:] for v in me.vertices])
samp=co[np.random.default_rng(0).choice(len(co),400,replace=False)]
def dtm_T(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.clip(np.round(fy),0,499)); i=int(np.clip(np.round(fx),0,499)); return float(DT[j,i])
e1=np.median([abs(dtm(x,y)-z) for x,y,z in samp]); 
DTt=DT.T.copy(); 
def dtmT(x,y):
    global DT
    S=DT; DT=DTt; r=dtm(x,y); DT=S; return r
e2=np.median([abs(dtmT(x,y)-z) for x,y,z in samp]); e3=np.median([abs(dtm(x,-y)-z) for x,y,z in samp])
print('E114f orient err rowY %.2f T %.2f flipY %.2f'%(e1,e2,e3))
F=dtm if e1<=min(e2,e3) else (dtmT if e2<=e3 else (lambda x,y: dtm(x,-y)))
X0,X1,Y0,Y1=-132,48,-251,-228
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
dele=[]
for f in bm.faces:
    vs=[v.co for v in f.verts]
    if not all(X0<v.x<X1 and Y0<v.y<Y1 for v in vs): continue
    if max((f.verts[i].co.xy-f.verts[i-1].co.xy).length for i in range(len(vs)))>6.0: dele.append(f)
tris=[[tuple(v.co.xy) for v in f.verts] for f in dele]; tmat=[f.material_index for f in dele]
print('E114f fan faces',len(dele))
# rasterize hole cells (cell [x,x+1]x[y,y+1]) whose centre lies inside a deleted face (buffer by testing 5 pts)
class Path:
    def __init__(s,poly): s.p=np.array(poly)
    def contains_points(s,pts):
        m=np.zeros(len(pts),bool); a=s.p[0]
        for k in range(1,len(s.p)-1):
            b=s.p[k]; c=s.p[k+1]
            v0=c-a; v1=b-a; v2=pts-a
            d00=v0@v0; d01=v0@v1; d11=v1@v1; d02=v2@v0; d12=v2@v1; den=d00*d11-d01*d01
            if abs(den)<1e-12: continue
            u=(d11*d02-d01*d12)/den; v=(d00*d12-d01*d02)/den
            m|=(u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)
        return m
cells={}
for tr,mi_ in zip(tris,tmat):
    P=Path(tr); xs=[p[0] for p in tr]; ys=[p[1] for p in tr]
    gx,gy=np.meshgrid(np.arange(np.floor(min(xs))-1,np.ceil(max(xs))+1),np.arange(np.floor(min(ys))-1,np.ceil(max(ys))+1))
    for ox,oy in ((0.5,0.5),(0.05,0.05),(0.95,0.05),(0.05,0.95),(0.95,0.95)):
        pts=np.c_[gx.ravel()+ox,gy.ravel()+oy]; m=P.contains_points(pts)
        for x,y in zip(gx.ravel()[m],gy.ravel()[m]): cells.setdefault((int(x),int(y)),mi_)
print('E114f cells',len(cells))
bmesh.ops.delete(bm,geom=dele,context='FACES_ONLY')
bm.to_mesh(me); bm.free(); me.update()
# patch
pb=bmesh.new(); V={}
def gv(x,y):
    k=(x,y)
    if k not in V: V[k]=pb.verts.new((x,y,F(x,y)-0.01))
    return V[k]
for (x,y),mi_ in cells.items():
    f=pb.faces.new((gv(x,y),gv(x+1,y),gv(x+1,y+1),gv(x,y+1))); f.material_index=mi_
uvl=pb.loops.layers.float_vector.new('ortho') if False else None
pm=bpy.data.meshes.new('WS114_terrain_fan_fill_S_edge_DTM1m'); pb.to_mesh(pm); pb.free()
gp=next(o for o in bpy.data.objects if o.name.startswith('WS110_ground_patch'))
for m in me.materials: pm.materials.append(m)
oa=pm.attributes.new('ortho','FLOAT2','CORNER')
for l in pm.loops:
    v=pm.vertices[l.vertex_index].co; oa.data[l.index].vector=(v.x/500+0.5,v.y/500+0.5)
print('E114f patch mats',dict(zip(*np.unique(list(cells.values()),return_counts=True))))
po=bpy.data.objects.new('WS114_terrain_fan_fill_S_edge_DTM1m_UNVERIFIEDgrade',pm)
(t.users_collection[0]).objects.link(po)
# paving proxy for the clamp: all meshes (non terrain/building/tree) with upward faces overlapping the patch area within +-0.6 m of DTM
B=[]
pv=bpy.data.objects['WS113_paving_tops_proxy']; pbm=bmesh.new(); pbm.from_mesh(pv.data); n0=len(pbm.faces)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o in (t,po,gp,pv) or o.name.startswith('WS113_terrain_fan_fill'): continue
    nm=o.name
    if nm.startswith(('T_','Terrain','Context_skirt','OZ_','WS111_entrance','WS107_Chapin','WS108','Chapin')) or 'roof' in nm.lower() or 'wall' in nm.lower() or 'tree' in nm.lower() or 'shrub' in nm.lower(): continue
    EV=bool(o.modifiers)
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if len(o.data.polygons)>400000: continue
    dg=bpy.context.evaluated_depsgraph_get(); src=o.evaluated_get(dg).to_mesh() if EV else o.data
    tb=bmesh.new(); tb.from_mesh(src); tb.transform(o.matrix_world); tb.normal_update()
    if EV: o.evaluated_get(dg).to_mesh_clear()
    keep=[]
    for f in tb.faces:
        if f.normal.z<0.7: continue
        c=f.calc_center_median()
        if not (X0<c.x<X1 and Y0<c.y<Y1 and (int(np.floor(c.x)),int(np.floor(c.y))) in cells): continue
        dz=c.z-F(c.x,c.y)
        if abs(dz)>0.6 or (EV and not (-0.12<dz<0.25)): continue
        keep.append(f)
    if keep:
        bmesh.ops.delete(tb,geom=[f for f in tb.faces if f not in set(keep)],context='FACES')
        tm=bpy.data.meshes.new('tmp'); tb.to_mesh(tm); pbm.from_mesh(tm); bpy.data.meshes.remove(tm); B.append((nm,len(keep)))
    tb.free()
pbm.to_mesh(pv.data); pbm.free(); pv.data.update()
print('E114f paving added to proxy',B[:30],'total',len(B))
m=po.modifiers.new('WS113_paving_edge_grade','NODES'); m.node_group=bpy.data.node_groups['WS113_paving_edge_grade']
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('E114 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('E114 SAVED',SAVE)

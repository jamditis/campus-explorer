# ws141c (fast numpy version of 141b): ortho-drape ground under the BK NE-corner tree -> lawn; lawn feathered flush to the pad edges
import bpy, bmesh, os, numpy as np
from mathutils import Vector, kdtree
OB=bpy.data.objects
LAWN=bpy.data.materials['COLE_lawn_post2020_bs']
REG=(-88,-74.75,-216.6,-202.5)
def isortho(m):
    if m is None: return False
    n=m.name.lower()
    return ('ortho' in n) and not any(k in n for k in ('asphalt','walk','curb','paint','road','concrete','brick','roof'))
NE=np.array([-73.2,-218.5]); NW=np.array([-88.3,-214.9])
def nface(x): return NE[1]+(NW[1]-NE[1])*(x-NE[0])/(NW[0]-NE[0])
pad=[o for o in OB if o.name.startswith('WS141_BK_NE_concrete_pad')][0]; pmw=pad.matrix_world
bmp=bmesh.new(); bmp.from_mesh(pad.data); B=[]
for e in bmp.edges:
    if any(f.normal.z>0.5 for f in e.link_faces) and any(abs(f.normal.z)<0.5 for f in e.link_faces):
        B+= [pmw@e.verts[0].co, pmw@e.verts[1].co]
bmp.free()
BA=np.array([[p.x,p.y,p.z] for p in B]); T=kdtree.KDTree(len(B))
for i_,p in enumerate(B): T.insert(Vector((p.x,p.y,0)),i_)
T.balance()
xe_max=BA[:,0].max()
def inside(x,y):
    nf=nface(x)
    A=(-74.6<=x<=xe_max) and (nf-0.12<=y<=-205.0)
    Bq=(-78.5<=x<=-74.6) and (nf-0.05<=y<=nf+2.26)
    return A or Bq
tex={}; gr={}
for o in OB:
    if o.type!='MESH' or not o.name.startswith(('Terrain','WS114','WS134_ground','WS133b_ground','WS110_ground')): continue
    me=o.data; mw=np.array(o.matrix_world); n=len(me.vertices)
    co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    W=co@mw[:3,:3].T+mw[:3,3]
    # ortho faces -> lawn
    mats=list(me.materials)
    oi=[i for i,m in enumerate(mats) if isortho(m)]
    if oi:
        npl=len(me.polygons); c=np.empty(npl*3); me.polygons.foreach_get('center',c); c=c.reshape(-1,3)@mw[:3,:3].T+mw[:3,3]
        mi_=np.empty(npl,dtype=np.int32); me.polygons.foreach_get('material_index',mi_)
        sel=np.isin(mi_,oi)&(c[:,0]>REG[0])&(c[:,0]<REG[1])&(c[:,1]>REG[2])&(c[:,1]<REG[3])
        if sel.any():
            li=next((i for i,m in enumerate(mats) if m==LAWN),None)
            if li is None: me.materials.append(LAWN); li=len(me.materials)-1
            mi_[sel]=li; me.polygons.foreach_set('material_index',mi_); tex[o.name[:40]]=int(sel.sum())
    # feather
    m=(W[:,0]>-80.2)&(W[:,0]<xe_max+0.2)&(W[:,1]>-220.5)&(W[:,1]<-203.4)
    idx=np.nonzero(m)[0]; k=0
    for i in idx:
        x,y,z=W[i]
        _c,j,d=T.find(Vector((x,y,0)))
        if d>1.5 or inside(x,y): continue
        zt=BA[j,2]-0.025
        if abs(z-zt)>0.6: continue
        w=1.0 if d<0.6 else (1.5-d)/0.9
        W[i,2]=z+(zt-z)*w; k+=1
    if k:
        L=(W-mw[:3,3])@np.linalg.inv(mw[:3,:3]).T
        me.vertices.foreach_set('co',L.ravel()); me.update(); gr[o.name[:40]]=k
    elif o.name[:40] in tex: me.update()
print('RETEX',tex); print('FEATHER',gr)
bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True); print('SAVED')

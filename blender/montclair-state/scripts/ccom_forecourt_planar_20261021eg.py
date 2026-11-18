# Session eg (Oct 21 2026 ~8:35 PM ET): the CCOM west-entrance herringbone forecourt was draped on the 1 m DTM and humped
# ~12-17 cm along its south edge (ef/ed self-review). Real forecourts are near-planar: replace the paving z with a least-squares
# plane (gentle ~3% fall away from the door, drainage) anchored to the door centre at 137.60 (threshold top 137.61) and capped
# at 137.60 so it never rises above the threshold. Then re-run the ed edge-clean (skirt rebuild + terrain under paving) and
# ed lawn-edge (grass/lawn eased to the new edge, from their stored original z) and reseat the 3 photo bins by the local dz.
# Orig paving z in point attribute eg_orig_z, bin dz in custom prop eg_dz. SAVE=1 saves; REVERT=1 restores (then rerun ed scripts).
import bpy, os, runpy, numpy as np, mathutils
from mathutils.bvhtree import BVHTree
HERE=os.path.dirname(os.path.abspath(__file__))
fc=bpy.data.objects['CCOM brick forecourt (ortho + photo)']; me=fc.data; mw=fc.matrix_world; inv=mw.inverted()
REV=os.environ.get('REVERT')=='1'; SAVE=os.environ.get('SAVE')=='1'
def zat(x,y):
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    h=b.ray_cast(mathutils.Vector((x,y,200)),mathutils.Vector((0,0,-1))); return h[0].z if h[0] else None
bins=[o for o in bpy.data.objects if o.name.startswith('CCOM entrance bin ')]
z_before={o.name:zat(o.matrix_world.translation.x,o.matrix_world.translation.y) for o in bins}
a=me.attributes.get('eg_orig_z')
if REV:
    if a:
        for v,o in zip(me.vertices,a.data): v.co.z=o.value
        me.attributes.remove(a)
    for o in bins:
        if 'eg_dz' in o: o.location.z-=o['eg_dz']; del o['eg_dz']
    print('EG_REVERTED')
else:
    if a is None:
        a=me.attributes.new('eg_orig_z','FLOAT','POINT')
        for v,d in zip(me.vertices,a.data): d.value=v.co.z
    P=np.array([tuple(mw@mathutils.Vector((v.co.x,v.co.y,d.value))) for v,d in zip(me.vertices,a.data)])
    X0,Y0,Z0=-20.06,11.78,float(os.environ.get('ZDOOR','137.60'))
    A=np.c_[P[:,0]-X0,P[:,1]-Y0]; ab,*_=np.linalg.lstsq(A,P[:,2]-Z0,rcond=None)
    zn=np.minimum(Z0+A@ab,Z0)
    for v,z,p in zip(me.vertices,zn,P): v.co=inv@mathutils.Vector((p[0],p[1],z))
    me.update()
    print('EG_PLANE slope a,b',ab,'z range',zn.min(),zn.max(),'dz range',(zn-P[:,2]).min(),(zn-P[:,2]).max())
os.environ.pop('SAVE',None); os.environ.pop('REVERT',None)
runpy.run_path(os.path.join(HERE,'ccom_forecourt_edge_clean_20261021ed.py'),run_name='__main__')
runpy.run_path(os.path.join(HERE,'ccom_forecourt_lawn_edge_20261021ed.py'),run_name='__main__')

# eg fill: where the lawn now sits below the planar paving edge, ease terrain + grass up within 1.6 m outside the edge
# (z >= edge_z - 0.03 - 0.15*d); grass within 0.25 m of the edge stays sunk. Pre-fill z in point attribute eg3_orig_z.
import re, bmesh as _bm
_b=_bm.new(); _b.from_mesh(me); _b.transform(mw); _bvh=BVHTree.FromBMesh(_b)
_bnd=[(e.verts[0].co.copy(),e.verts[1].co.copy()) for e in _b.edges if e.is_boundary]
_xs=[v.co.x for v in _b.verts]; _ys=[v.co.y for v in _b.verts]
def _edge(p):
    best=(1e9,None)
    for a_,b_ in _bnd:
        a2=a_.xy; b2=b_.xy; ab_=b2-a2; t=max(0,min(1,(p.xy-a2).dot(ab_)/ab_.length_squared)); q=a2+ab_*t
        d=(p.xy-q).length
        if d<best[0]: best=(d,a_.z+(b_.z-a_.z)*t)
    return best
_t=[bpy.data.objects['Terrain_LiDAR_DTM_1m']]+[o for o in bpy.data.objects if o.type=='MESH' and re.match(r'(?i)^(dS_grass|cx_grass|cd_grass|Lawn_grass_instanced)',o.name)]
for o in _t:
    m=o.data; ow=o.matrix_world; oi=ow.inverted(); grass=o.name!='Terrain_LiDAR_DTM_1m'
    at=m.attributes.get('eg3_orig_z')
    if REV:
        if at:
            for v,d in zip(m.vertices,at.data):
                if d.value>-9000: v.co.z=d.value
            m.attributes.remove(at); m.update(); print('EG3_REVERT',o.name)
        continue
    if at is None:
        at=m.attributes.new('eg3_orig_z','FLOAT','POINT'); at.data.foreach_set('value',[-9999.0]*len(m.vertices))
    n=0
    for i,v in enumerate(m.vertices):
        w=ow@v.co
        if not (min(_xs)-1.7<w.x<max(_xs)+1.7 and min(_ys)-1.7<w.y<max(_ys)+1.7): continue
        if _bvh.ray_cast(mathutils.Vector((w.x,w.y,w.z+30)),mathutils.Vector((0,0,-1)))[0] is not None: continue
        d,ez=_edge(w)
        if d>1.6 or (grass and d<0.25): continue
        base=at.data[i].value if at.data[i].value>-9000 else v.co.z
        zf=max(base, ez-0.03-0.15*d)
        if abs(zf-w.z)>1e-5:
            if at.data[i].value<-9000: at.data[i].value=v.co.z
            v.co.z=(oi@mathutils.Vector((w.x,w.y,zf))).z; n+=1
    m.update(); print('EG3_FILL',o.name,'raised',n)
if not REV:
    for o in bins:
        t=o.matrix_world.translation; zb=z_before[o.name]; za=zat(t.x,t.y)
        if zb is not None and za is not None:
            dz=za-zb; o.location.z+=dz; o['eg_dz']=o.get('eg_dz',0)+dz; print('EG_BIN',o.name,round(dz,3))
    # edge step report: terrain 0.3/1.0 m outside each boundary vertex vs paving edge
    import bmesh
    ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tb=bmesh.new(); tb.from_mesh(ter.data); tb.transform(ter.matrix_world); tv=BVHTree.FromBMesh(tb)
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(mw); c=sum((v.co for v in bm.verts),mathutils.Vector())/len(bm.verts)
    st=[]
    for v in bm.verts:
        if not v.is_boundary: continue
        d=(v.co-c); d.z=0; d.normalize()
        for off in (0.3,1.0,1.5):
            q=v.co+d*off; h=tv.ray_cast(mathutils.Vector((q.x,q.y,200)),mathutils.Vector((0,0,-1)))
            if h[0]: st.append((off,h[0].z-v.co.z,round(v.co.x,1),round(v.co.y,1)))
    for off in (0.3,1.0,1.5):
        s=[x for x in st if x[0]==off]; s.sort(key=lambda x:x[1])
        print('EG_STEP off',off,'terrain-paving min',s[0],'max',s[-1])
if SAVE: bpy.ops.wm.save_mainfile(); print('EG_SAVED')

# pn: level the old Feliciano wall tops (sloped LiDAR-derived tops read as diagonal seams) to the pn tier height just inside each
# wall face (ray down 0.45 m inside), never raising a wall and never below its highest window head + 0.35 m. Reversible mesh swap
# (prop pn_prev_mesh). UNVERIFIED.
import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
w=bpy.data.objects['Feliciano School of Business walls']
if 'pn_prev_mesh' in w.keys():
    old=w.data; w.data=bpy.data.meshes[w['pn_prev_mesh']]; del w['pn_prev_mesh']; bpy.data.meshes.remove(old); print('REVERTED_PN_WALLTOPS')
if not REV:
    col=bpy.data.collections['PN_Feliciano_remass_20261101pn_UNVERIFIED']
    V=[];F=[]
    for o in col.objects:
        if not o.name.startswith('PN_Feliciano_tier_'): continue
        mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    T=BVHTree.FromPolygons(V,F)
    WV=[];WF=[]
    for o in bpy.data.objects:
        if o.type=='MESH' and not o.hide_render and 'indows' in o.name and 'Feliciano' in o.name and not o.name.startswith('PN_'):
            mw=o.matrix_world; b=len(WV); WV+=[mw@v.co for v in o.data.vertices]; WF+=[[b+i for i in p.vertices] for p in o.data.polygons]
    WT=BVHTree.FromPolygons(WV,WF)
    prev=w.data; me=prev.copy(); me.name=prev.name+'_pn'; mw=w.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    bmesh.ops.split_edges(bm,edges=[e for e in bm.edges if abs((mw@e.verts[0].co).z-(mw@e.verts[1].co).z)>0.5])
    C=Vector((-225.3,194.2,0)); low=0; skip=0
    for f in bm.faces:
        vs=sorted(f.verts,key=lambda v:(mw@v.co).z); tops=vs[2:]; bots=vs[:2]
        c=mw@f.calc_center_median(); n=(mw.to_3x3()@f.normal); n=Vector((n.x,n.y,0)).normalized()
        if n.dot(c-C)<0: n=-n
        q=Vector((c.x,c.y,200))-n*0.45
        h=T.ray_cast(q,Vector((0,0,-1)),100)
        if h[0] is None: skip+=1; continue
        zt=h[0].z
        # highest window head on this face
        wz=-1e9
        for t in (0.1,0.3,0.5,0.7,0.9):
            p=(mw@bots[0].co).lerp(mw@bots[1].co,t)
            for z in [x*0.5 for x in range(int(2*140),int(2*168))]:
                hh=WT.find_nearest(Vector((p.x,p.y,z)),0.6)
                if hh[0] is not None: wz=max(wz,hh[0].z)
        zt=max(zt,wz+0.35)
        for v in tops:
            wv=mw@v.co
            if wv.z>zt+0.02: wv.z=zt; v.co=mi@wv; low+=1
    bm.to_mesh(me); bm.free(); w['pn_prev_mesh']=prev.name; prev.use_fake_user=True; w.data=me
    print('PN_WALLTOPS lowered verts',low,'skipped faces',skip)
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

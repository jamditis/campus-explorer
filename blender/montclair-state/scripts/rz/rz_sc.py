# rz (Student Center): append the north-file Student Center hero pass (Oct 14 r/t/u + Oct 15 av) into MAIN.
# Same EPSG:6527 local frame as north (qm precedent: no transform). Hides MAIN placeholder objects inside the footprint
# (none expected), culls QV/QX grass points inside the OSM 313026743 footprint (+0.5 m), saving removed coords for revert.
# ALL UNVERIFIED. REVERT=1 removes everything appended (data/rz/sc_added.json) and restores culled points.
import bpy, os, json, bmesh
import numpy as np
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; J='data/rz/sc_added.json'; PARENT='RZ_StudentCenter_hero_from_north_UNVERIFIED'
CN=['North_StudentCenter_20261014r','North_StudentCenter_facade_20261014t','North_StudentCenter_court_20261014u','North_StudentCenter_wing_rhythm_20261015av']
fp=json.load(open('data/qr/day8_prep/student_center_footprints_local_qr.json'))['ways']['313026743']['pts_local_m']
P=np.array(fp)
def inside(x,y,poly=P):
    n=len(poly); c=np.zeros(len(x),bool); j=n-1
    for i in range(n):
        xi,yi=poly[i]; xj,yj=poly[j]
        m=((yi>y)!=(yj>y)) & (x < (xj-xi)*(y-yi)/((yj-yi)+1e-12)+xi)
        c^=m; j=i
    return c
def grow(poly,d=0.5):
    cx,cy=poly[:-1].mean(0); v=poly-[cx,cy]; r=np.linalg.norm(v,axis=1,keepdims=True); return [cx,cy]+v*(1+d/np.maximum(r,1))
PG=grow(P,0.5)
if os.path.exists(J) and (REV or bpy.data.collections.get(PARENT)):
    d=json.load(open(J))
    for n in d['objects']:
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True)
    for k in ('collections','meshes','materials','node_groups','images'):  # libraries NOT removed (removing it dropped 665 pre-existing linked objects in the rz revert test)
        for n in d.get(k,[]):
            x=getattr(bpy.data,k).get(n)
            if x and (k=='collections' or x.users==0): getattr(bpy.data,k).remove(x)
    for n,(hr,hv) in d['hidden'].items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    if os.path.exists('data/rz/grass_removed.npz'):
        z=np.load('data/rz/grass_removed.npz')
        for n in d['culled']:
            o=bpy.data.objects.get(n); a=z[n.replace(' ','_')]
            if o is None or len(a)==0: continue
            me=o.data; k0=len(me.vertices); me.vertices.add(len(a)); me.vertices.foreach_set('co',np.concatenate([np.array([v.co[:] for v in me.vertices[:k0]]).ravel(),a.ravel()])) if False else None
            for i,co in enumerate(a): me.vertices[k0+i].co=co
            me.update()
    print('RZ_SC reverted')
if not REV:
    before={k:set(x.name for x in getattr(bpy.data,k)) for k in ('objects','meshes','materials','collections','libraries','node_groups','images')}
    with bpy.data.libraries.load('north/montclair_north.blend',link=False) as (a,b): b.collections=[c for c in a.collections if c in CN]
    par=bpy.data.collections.new(PARENT); bpy.context.scene.collection.children.link(par)
    for c in b.collections:
        # skip children already present elsewhere (nested duplicates)
        if not any(c.name in [x.name for x in p.children_recursive] for p in b.collections if p!=c): par.children.link(c)
    new=set(par.all_objects)
    # hide main placeholders whose bbox centre lies inside the footprint (excluding new + ground/grass/terrain)
    hid={}
    for o in bpy.data.objects:
        if o in new or o.type!='MESH' or o.hide_render: continue
        if any(s in o.name for s in ('errain','skirt','grass','Grass','QXP','QX_','QY_','QV_','QW_','ortho','Roads','Footpaths','QS_')): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
        dx=max(v.x for v in bb)-min(v.x for v in bb)
        if dx<200 and inside(np.array([cx]),np.array([cy]))[0]:
            hid[o.name]=(o.hide_render,o.hide_viewport); o.hide_render=True; o.hide_viewport=True
    print('RZ hidden',list(hid)[:30])
    # cull grass points
    culled={}; 
    for o in bpy.data.objects:
        if o.type=='MESH' and 'grass' in o.name.lower() and 'point' in o.name.lower() and len(o.data.polygons)==0:
            me=o.data; n=len(me.vertices)
            co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
            w=np.array(o.matrix_world); wc=co@w[:3,:3].T+w[:3,3]
            m=inside(wc[:,0],wc[:,1],PG)
            if m.sum()==0: continue
            culled[o.name.replace(' ','_')]=co[m]
            bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm,geom=[bm.verts[i] for i in np.nonzero(m)[0]],context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
            print('RZ culled',o.name,int(m.sum()),'of',n)
    np.savez('data/rz/grass_removed.npz',**culled)
    # lettering was parented in north? no: its world matrix did not survive the append -> set it from north (probe_n.log)
    from mathutils import Matrix
    LM=Matrix(((0.9222578406333923,1.3858491243468052e-08,-0.3865751624107361,-9.774213790893555),(-0.3865751624107361,7.605307672520212e-08,-0.9222578406333923,292.465087890625),(1.661912918393682e-08,1.0,7.549789415861596e-08,150.18045043945312),(0,0,0,1)))
    for o in par.all_objects:
        if o.name.startswith('SC lettering'): o.matrix_world=LM; print('RZ lettering placed')
    # the appended copy of the north ortho points at a broken relative path -> remap to MAIN's repathed copy (qo)
    for i in list(bpy.data.images):
        if i.name not in before['images'] and i.name.startswith('ortho2020_north.jpg') and bpy.data.images.get('ortho2020_north.jpg.001'):
            i.user_remap(bpy.data.images['ortho2020_north.jpg.001']); bpy.data.images.remove(i); print('RZ image remapped')
    for l in list(bpy.data.libraries):
        if l.name not in before['libraries'] and l.users==0: bpy.data.libraries.remove(l); print('RZ empty lib removed')
    for o in par.all_objects: o['UNVERIFIED_rz']='rz: Student Center hero pass appended from north (Oct 14 r/t/u, Oct 15 av)'
    after={k:set(x.name for x in getattr(bpy.data,k)) for k in before}
    d={k:sorted(after[k]-before[k]) for k in before}; d['hidden']=hid; d['culled']=[k for k in culled]
    json.dump(d,open(J,'w'),indent=0)
    xs=[ (o.matrix_world@Vector(c)) for o in par.all_objects if o.type=='MESH' for c in o.bound_box]
    print('RZ_SC appended',{k:len(v) for k,v in d.items() if isinstance(v,list)},'bbox',min(v.x for v in xs),max(v.x for v in xs),min(v.y for v in xs),max(v.y for v in xs),min(v.z for v in xs),max(v.z for v in xs))
    print('libs',[l.filepath for l in bpy.data.libraries])
    print('OBJCOUNT',len(bpy.data.objects))
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

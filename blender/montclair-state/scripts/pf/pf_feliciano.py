# pf (Nov 1 2026, day 6): Feliciano School of Business in MAIN. REVERT=1 undoes everything. Mostly UNVERIFIED (detail per refs feliciano_commons_07/08 via north scene).
# (A) MAIN terrain around Feliciano was the unmeasured LiDAR-disc 'fan' and sat ~2.5-3.5 m ABOVE the real ground (USGS LiDAR DTM p50 134.0 inside the footprint,
#     north/data/oq_prep/feliciano_survey_oe.json; North_terrain_LiDAR_1m = real 1 m LiDAR, matches MAIN exactly inside the disc e.g. (0,100) 138.06).
#     Removable GN modifier PF_terrain_feliciano_lidar on Terrain_LiDAR_DTM_1m (after PB): fan faces touching the box are subdivided and moved onto a cropped copy of
#     the north LiDAR terrain (PF_north_LiDAR_DTM_ref_feliciano, hidden) with a feathered box weight and w=0 at the seam with unmoved faces.
# (B) north-scene Feliciano detail (entrance pavilion, arcades, pent roofs, gold lettering, date stones, forecourt, 8 window groups) ported; trees in the box re-seated.
import bpy, os, sys, bmesh, mathutils
NORTH='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
TOP='PF_Feliciano_port_20261101pf_UNVERIFIED'; MN='PF_terrain_feliciano_lidar'; NG=MN+'_GN'; REF='PF_north_LiDAR_DTM_ref_feliciano'
COLLS=['North_Feliciano_entrance_20261013','North_Feliciano_forecourt_20261014b','North_Feliciano_windows_20261014']
CAMS={'CAM_closeup_feliciano':'PF_CAM_closeup_feliciano_entrance','CAM_closeup_feliciano_forecourt':'PF_CAM_eye_feliciano_forecourt',
      'CAM_eye_feliciano_east_bg':'PF_CAM_eye_feliciano_east','CAM_oblique_uh_feliciano_bg':'PF_CAM_oblique_feliciano_from_E'}
E=os.environ.get; X0,X1,Y0,Y1=[float(q) for q in E('BOX','-275,-186,134,250').split(',')]; FB=float(E('FB','8')); FW=float(E('FW','6')); LEVEL=int(E('LEVEL','6'))
sc=bpy.context.scene; T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def save(): bpy.ops.wm.save_mainfile()
if E('REVERT')=='1':
    for o in bpy.data.objects:
        if 'pf_dz' in o: o.location.z-=o['pf_dz']; del o['pf_dz']
    if MN in T.modifiers: T.modifiers.remove(T.modifiers[MN])
    if T.get('pf_prev_mesh'):
        o_=bpy.data.meshes[T['pf_prev_mesh']]; n_=T.data; T.data=o_; o_.use_fake_user=False; del T['pf_prev_mesh']
        if n_.users==0: bpy.data.meshes.remove(n_)
    if 'pf_terrain_feliciano' in T: del T['pf_terrain_feliciano']
    if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
    top=bpy.data.collections.get(TOP)
    if top:
        def walk(c):
            for ch in list(c.children): walk(ch)
            for o in list(c.objects):
                d=o.data; bpy.data.objects.remove(o)
            bpy.data.collections.remove(c)
        walk(top)
    pass  # no orphans_purge: it removed 665 unrelated kept objects (Sprague, CafeDiem)
    save(); print('PF_REVERT_DONE',len(bpy.data.objects)); raise SystemExit
assert TOP not in bpy.data.collections
dg=bpy.context.evaluated_depsgraph_get()
def tz(x,y):
    te=T.evaluated_get(bpy.context.evaluated_depsgraph_get()); mi=T.matrix_world.inverted()
    h,loc,n,i=te.ray_cast(mi@mathutils.Vector((x,y,400)),(0,0,-1))
    return (T.matrix_world@loc).z if h else None
trees=[]
for o in sc.objects:
    if o.users_collection and o.users_collection[0].name=='Trees_assets_LiDAR':
        x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
        if X0<x<X1 and Y0<y<Y1: trees.append((o,tz(x,y)))
with bpy.data.libraries.load(NORTH, link=False) as (src,dst):
    dst.collections=[c for c in COLLS if c in src.collections]
    dst.objects=[c for c in CAMS if c in src.objects]+['North_terrain_LiDAR_1m']
top=bpy.data.collections.new(TOP); sc.collection.children.link(top)
for c in dst.collections: top.children.link(c)
refc=bpy.data.collections.new('PF_terrain_ref_hidden'); top.children.link(refc)
for o in dst.objects:
    if o.name.startswith('North_terrain'):
        o.name=REF; refc.objects.link(o); me=o.data; me.name=REF+'_mesh'; me.materials.clear()
        bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world
        kill=[v for v in bm.verts if not (X0-12<(mw@v.co).x<X1+12 and Y0-12<(mw@v.co).y<Y1+12)]
        bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(me); bm.free()
        o.hide_render=True; o.hide_viewport=True; o.hide_set(True); print('REF verts',len(me.vertices))
        ref=o
    else:
        o.name=CAMS[o.name]; top.objects.link(o)
# forecourt slabs/pavers just above the draped OSM walks (+3 cm + 4 mm joints)
for c in dst.collections:
    for o in c.objects:
        if 'forecourt' in o.name and ('pavers' in o.name or 'concrete' in o.name): o.location.z+=0.05; print('LIFT',o.name[:40])
# ---- terrain: reversible mesh swap (old mesh kept with fake user, key pf_prev_mesh). Faces covering the box are chopped on a STEP m grid
# (bisect, box-local only), then verts inside the box move onto the real LiDAR heights (ray cast on the cropped north terrain) with a feathered box weight.
STEP=float(E('STEP','2.0'))
old=T.data; new=old.copy(); new.name=old.name+'_pf'
bm=bmesh.new(); bm.from_mesh(new); bm.faces.ensure_lookup_table()
mw=T.matrix_world; mi=mw.inverted()
def fbox(f):
    xs=[(mw@v.co).x for v in f.verts]; ys=[(mw@v.co).y for v in f.verts]
    return max(xs)>X0 and min(xs)<X1 and max(ys)>Y0 and min(ys)<Y1
XS=sorted(set([X0+i*STEP for i in range(int((X1-X0)/STEP)+1)]+[X1])); YS=sorted(set([Y0+i*STEP for i in range(int((Y1-Y0)/STEP)+1)]+[Y1]))
planes=[(mathutils.Vector((x,0,0)),mathutils.Vector((1,0,0))) for x in XS]+[(mathutils.Vector((0,y,0)),mathutils.Vector((0,1,0))) for y in YS]
n0=len(bm.faces)
# keep the surface EXACT outside the box: rebuild every face touching the box (incl. non-planar quads/n-gons) as the triangles Blender actually
# evaluates (mesh loop_triangles) before cutting; cutting planar triangles cannot change heights.
old.calc_loop_triangles(); bm.verts.ensure_lookup_table()
touch={f.index for f in bm.faces if fbox(f) and len(f.verts)>3}

tris=[tuple(lt.vertices) for lt in old.loop_triangles if lt.polygon_index in touch]
mats={lt.polygon_index:old.polygons[lt.polygon_index].material_index for lt in old.loop_triangles if lt.polygon_index in touch}
tmat=[mats[lt.polygon_index] for lt in old.loop_triangles if lt.polygon_index in touch]
uvl=bm.loops.layers.uv
uvdata={}
for f in bm.faces:
    if f.index in touch:
        for l in f.loops: uvdata[(f.index,l.vert.index)]=[tuple(l[u].uv) for u in uvl.values()]
tpoly=[lt.polygon_index for lt in old.loop_triangles if lt.polygon_index in touch]
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in touch],context='FACES_ONLY')
bm.verts.ensure_lookup_table()
for (a_,b_,c_),mi_,pi_ in zip(tris,tmat,tpoly):
    f=bm.faces.new((bm.verts[a_],bm.verts[b_],bm.verts[c_])); f.material_index=mi_; f.smooth=True
    for l in f.loops:
        for k,u in enumerate(uvl.values()): l[u].uv=uvdata[(pi_,l.vert.index)][k]
print('RETRI faces',len(touch),'->',len(tris))
for co,no in planes:
    fs=[f for f in bm.faces if fbox(f)]
    if not fs: continue
    geom=list(set(fs)|{e for f in fs for e in f.edges}|{v for f in fs for v in f.verts})
    bmesh.ops.bisect_plane(bm,geom=geom,plane_co=mi@co,plane_no=(mi.to_3x3()@no).normalized(),dist=1e-4)
fs=[f for f in bm.faces if fbox(f)]

print('CHOP faces',n0,'->',len(bm.faces))
rme=ref.data; rmw=ref.matrix_world; rmi=rmw.inverted()
from mathutils.bvhtree import BVHTree
rb=bmesh.new(); rb.from_mesh(rme); rb.transform(rmw); bvh=BVHTree.FromBMesh(rb)
def ss(t): t=max(0.0,min(1.0,t)); return t*t*(3-2*t)
moved=0; dzs=[]
for v in bm.verts:
    p=mw@v.co
    if not (X0<p.x<X1 and Y0<p.y<Y1): continue
    w=ss((p.x-X0)/FB)*ss((X1-p.x)/FB)*ss((p.y-Y0)/FB)*ss((Y1-p.y)/FB)
    if w<=0: continue
    hit=bvh.ray_cast(mathutils.Vector((p.x,p.y,400)),mathutils.Vector((0,0,-1)))
    if hit[0] is None: continue
    dz=w*(hit[0].z-p.z); p.z+=dz; v.co=mi@p; moved+=1; dzs.append(dz)
rb.free(); bm.to_mesh(new); bm.free(); new.update()
old.use_fake_user=True; T['pf_prev_mesh']=old.name; T.data=new
import statistics
print('MOVED',moved,'dz min %.2f max %.2f mean %.2f'%(min(dzs),max(dzs),statistics.mean(dzs)))
# the ref terrain is only needed for the bake: remove it
refc.objects.unlink(ref); rmn=ref.data; bpy.data.objects.remove(ref); bpy.data.meshes.remove(rmn); bpy.data.collections.remove(refc)
T['pf_terrain_feliciano']='pf: terrain in box %s chopped on a %g m grid and moved onto USGS LiDAR 1 m (north terrain), feather %g m; old mesh %s'%((X0,X1,Y0,Y1),STEP,FB,old.name)
bpy.context.view_layer.update()
for x,y in [(-215,150),(-210,160),(-230,175),(-220,240),(-200,150),(-190,150),(-240,140)]: print('NEWZ',x,y,round(tz(x,y) or -1,2))
for o,z0 in trees:
    x,y=o.matrix_world.translation.x,o.matrix_world.translation.y; z1=tz(x,y)
    if z0 is not None and z1 is not None and abs(z1-z0)>0.01: o.location.z+=z1-z0; o['pf_dz']=z1-z0; print('TREE',o.name,round(z1-z0,2))
if '--save' in sys.argv: save()
print('PF_APPLY_DONE',len(bpy.data.objects))

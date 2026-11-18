import bpy,bmesh,json,os
from mathutils import Vector
B=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws98/build98.json'))
M=bpy.data.materials
def mat(*names):
    for n in names:
        if n in M: return M[n]
    print("A98 MISSING MAT",names); return None
ref=bpy.data.objects['WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']
coll=ref.users_collection[0]
def build(name,key,m,skirt):
    V,F=B[key]
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V],[],F); me.update()
    bm=bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    if skirt>0:
        bnd=[e for e in bm.edges if e.is_boundary]
        r=bmesh.ops.extrude_edge_only(bm,edges=bnd)
        nv=[v for v in r['geom'] if isinstance(v,bmesh.types.BMVert)]
        for v in nv: v.co.z-=skirt
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(name,me); coll.objects.link(o)
    if m: me.materials.append(m)
    print("A98 built",name,len(me.vertices),len(me.polygons))
    return o
build('WS98_lotE_entry_aisle_asphalt_OSMparkingaisle_LiDAR_ortho2020_UNVERIFIED','aisle',mat('fn_lot_asphalt'),0.15)
build('WS98_CollegeAve_bend_teardrop_island_MULCH_LiDAR_ortho2020_UNVERIFIED','island_mulch',mat('WS87_median_mulch_dark_JOEphoto'),0.12)
build('WS98_CollegeAve_bend_teardrop_island_CURB_LiDAR_UNVERIFIED','island_curb',mat('Kasser_apron_concrete_cm','WS27_curb_concrete_UNVERIFIED'),0.30)
build('WS98_lotE_raised_concrete_walk_pad_LiDAR15cm_curb_ortho2020_UNVERIFIED','pad',mat('Kasser_apron_concrete_cm'),0.35)
# curb cut at aisle mouth
C=bpy.data.objects['WS27_CollegeAve_curb_right_UNVERIFIED']; mw=C.matrix_world
cut={(round(a,2),round(b,2)) for a,b in B['curb_cut_centroids']}
bm=bmesh.new(); bm.from_mesh(C.data); bm.faces.ensure_lookup_table()
dl=[]
for f in bm.faces:
    c=mw@f.calc_center_median()
    if (round(c.x,2),round(c.y,2)) in cut: dl.append(f)
bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(C.data); bm.free(); C.data.update()
print("A98 curb faces cut",len(dl),"of",len(cut))
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=T.matrix_world; imw=mw.inverted()
for key in ('terrain_lower','terrain_raise'):
    for i,d in B[key]:
        v=T.data.vertices[i]; w=mw@v.co; w.z+=d; v.co=imw@w
T.data.update(); print("A98 terrain",len(B['terrain_lower']),len(B['terrain_raise']))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("A98 SAVED")
